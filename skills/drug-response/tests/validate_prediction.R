#!/usr/bin/env Rscript
# Validate the two prediction traps the skill warns about, on simulated data
# with a known ground truth: feature leakage and tissue confounding.
#
# Simulation, not a public panel, because the point is a controlled ground
# truth. Only 5 of 800 features carry signal; the rest are noise. Selecting
# features before cross-validation should inflate apparent accuracy, and a
# lineage-structured response should be predictable from lineage alone.
#
# Expected runtime: 1-2 minutes. No downloads.
# Requirements: glmnet

suppressPackageStartupMessages(library(glmnet))

cat("=== Drug Sensitivity Prediction Validation ===\n\n")
pass <- 0; fail <- 0

check <- function(name, condition) {
  if (isTRUE(condition)) {
    cat(sprintf("  PASS: %s\n", name)); pass <<- pass + 1
  } else {
    cat(sprintf("  FAIL: %s\n", name)); fail <<- fail + 1
  }
}

cat(sprintf("  glmnet %s\n\n", packageVersion("glmnet")))

# --- Feature leakage ---
set.seed(7)
n <- 120; p <- 800
X <- matrix(rnorm(n * p), n, p)
signal <- 1:5
beta <- c(rep(1.5, 5), rep(0, p - 5))     # only 5 genes matter
y <- as.numeric(X %*% beta + rnorm(n, 0, 3))

# WRONG: select top-correlated features on the full data, then cross-validate.
cors <- abs(cor(X, y))
top <- order(cors, decreasing = TRUE)[1:20]
cv_leak <- cv.glmnet(X[, top], y, alpha = 0.5, nfolds = 5)
pred_leak <- predict(cv_leak, X[, top], s = "lambda.min")
r_leak <- as.numeric(cor(pred_leak, y))

# RIGHT: selection inside each fold, so the test fold is never seen.
folds <- sample(rep(1:5, length.out = n))
preds <- numeric(n)
for (k in 1:5) {
  tr <- folds != k; te <- folds == k
  ck <- abs(cor(X[tr, ], y[tr]))
  tk <- order(ck, decreasing = TRUE)[1:20]
  m <- cv.glmnet(X[tr, tk], y[tr], alpha = 0.5, nfolds = 5)
  preds[te] <- predict(m, X[te, tk], s = "lambda.min")
}
r_proper <- as.numeric(cor(preds, y))

cat(sprintf("  leaky (select-then-CV) correlation : %.3f\n", r_leak))
cat(sprintf("  proper (nested CV)     correlation : %.3f\n", r_proper))
cat(sprintf("  inflation                          : %.3f\n", r_leak - r_proper))

# Values are seed-dependent, so assert the direction and a substantial gap,
# not an exact number.
check("Leaky selection reports higher accuracy than nested CV", r_leak > r_proper)
check("The inflation is substantial (> 0.15)", (r_leak - r_proper) > 0.15)
check("Nested CV still recovers real signal (r > 0)", r_proper > 0)

# The leak is not because it found the wrong genes: it found the right ones,
# but scored them on data they were selected from.
n_signal_leak <- sum(top %in% signal)
cat(sprintf("  real signal genes in the leaky top-20: %d of 5\n", n_signal_leak))
check("Leaky selection does find the true signal genes", n_signal_leak >= 4)

# --- Tissue confounding ---
# Response is determined ENTIRELY by lineage, with RANDOM per-lineage offsets
# (no cross-lineage trend a feature could generalize). Genes 1-5 are
# categorical lineage markers. A model can memorize each lineage's offset when
# it is present in training, but cannot predict a held-out lineage's offset,
# because nothing drug-specific was ever there to learn.
set.seed(11)
n2 <- 200; p2 <- 300
lineage <- factor(sample(1:5, n2, replace = TRUE))
offsets <- c(3.0, -2.0, 0.5, -3.5, 1.5)          # arbitrary, unordered
lin_off <- offsets[as.integer(lineage)]
X2 <- matrix(rnorm(n2 * p2), n2, p2)
for (g in 1:5) X2[, g] <- ifelse(as.integer(lineage) == g, 3, 0) + rnorm(n2, 0, 0.3)
y2 <- lin_off + rnorm(n2, 0, 0.4)                # response = lineage offset only

# Leave-lineage-out: hold out whole lineages, so the model cannot memorize
# a lineage's average response.
groups <- as.integer(lineage)
preds2 <- numeric(n2)
for (g in unique(groups)) {
  tr <- groups != g; te <- groups == g
  m <- cv.glmnet(X2[tr, ], y2[tr], alpha = 0.5, nfolds = 5)
  preds2[te] <- predict(m, X2[te, ], s = "lambda.min")
}
r_across <- as.numeric(cor(preds2, y2))

# Random-fold CV, which lets lineage leak between train and test.
set.seed(3)
folds2 <- sample(rep(1:5, length.out = n2))
preds2b <- numeric(n2)
for (k in 1:5) {
  tr <- folds2 != k; te <- folds2 == k
  m <- cv.glmnet(X2[tr, ], y2[tr], alpha = 0.5, nfolds = 5)
  preds2b[te] <- predict(m, X2[te, ], s = "lambda.min")
}
r_random <- as.numeric(cor(preds2b, y2))

cat(sprintf("\n  random-fold CV correlation    : %.3f\n", r_random))
cat(sprintf("  leave-lineage-out correlation : %.3f\n", r_across))

check("Random-fold CV looks highly accurate on lineage-confounded data",
      r_random > 0.7)
check("Leave-lineage-out collapses (gap > 0.5)", (r_random - r_across) > 0.5)
cat("    -> the model was predicting lineage, not drug-specific biology\n")
cat("       within-panel CV would have reported this as external validation\n")

cat(sprintf("\n=== Prediction: %d passed, %d failed ===\n", pass, fail))
if (fail > 0) quit(status = 1)

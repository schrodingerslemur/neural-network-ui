# Classification Loss Functions
nn.CrossEntropyLoss      # Multi-class classification, combines LogSoftmax and NLLLoss
nn.NLLLoss               # Negative Log Likelihood Loss, often used with LogSoftmax
nn.BCELoss               # Binary Cross Entropy Loss for binary classification
nn.BCEWithLogitsLoss     # Stable binary cross entropy, applies sigmoid internally
nn.MultiLabelMarginLoss  # Multi-label hinge loss for classification
nn.MultiLabelSoftMarginLoss # Multi-label classification with sigmoid and binary cross entropy
nn.MultiMarginLoss       # SVM-style margin-based loss for multi-class classification

# Regression Loss Functions
nn.MSELoss               # Mean Squared Error, commonly used in regression tasks
nn.L1Loss                # Mean Absolute Error for minimizing absolute differences
nn.SmoothL1Loss          # Huber Loss, a robust combination of MSE and MAE
nn.PoissonNLLLoss        # Poisson negative log likelihood, useful for count-based regression

# Ranking and Margin Loss Functions
nn.MarginRankingLoss     # Ranking loss with margin for comparing two inputs
nn.HingeEmbeddingLoss    # Hinge loss for binary classification tasks
nn.CosineEmbeddingLoss   # Cosine similarity-based loss for metric learning
nn.TripletMarginLoss     # Triplet loss for embedding learning

# Image and Sequence Reconstruction Losses
nn.KLDivLoss             # Kullback-Leibler Divergence for distribution matching
nn.CTCLoss               # Connectionist Temporal Classification, for sequence-to-sequence tasks

# Other Specialized Loss Functions
nn.HuberLoss             # Alias for Smooth L1 Loss, used in robust regression
nn.TripletMarginWithDistanceLoss # Variation of triplet loss with custom distance
nn.GaussianNLLLoss       # Gaussian negative log-likelihood for probabilistic regression

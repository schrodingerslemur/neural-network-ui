relu = nn.ReLU()                      # Applies f(x) = max(0, x)
leaky_relu = nn.LeakyReLU(0.01)       # Leaky ReLU with negative slope
prelu = nn.PReLU()                    # Parametric ReLU, slope is learned
elu = nn.ELU(alpha=1.0)               # Exponential Linear Unit
selu = nn.SELU()                      # Scaled Exponential Linear Unit
gelu = nn.GELU()                      # Gaussian Error Linear Unit
sigmoid = nn.Sigmoid()                # Applies sigmoid function f(x) = 1 / (1 + exp(-x))
tanh = nn.Tanh()                      # Applies hyperbolic tangent f(x) = (exp(x) - exp(-x)) / (exp(x) + exp(-x))
softmax = nn.Softmax(dim=1)           # Softmax for multi-class classification
log_softmax = nn.LogSoftmax(dim=1)    # Log(Softmax(x)), often used with NLLLoss
softplus = nn.Softplus()              # Smooth approximation to ReLU
softsign = nn.Softsign()              # Applies f(x) = x / (1 + |x|)
hardtanh = nn.Hardtanh(-1, 1)         # Hard tanh, clips values between -1 and 1
hardshrink = nn.Hardshrink(0.5)       # Hard shrinkage, sets values to 0 if |x| < lambda
softshrink = nn.Softshrink(0.5)       # Soft shrinkage, similar to hardshrink
relu6 = nn.ReLU6()                    # ReLU capped at 6
hardsigmoid = nn.Hardsigmoid()        # Efficient approximation of sigmoid
hardswish = nn.Hardswish()            # Applies f(x) = x * ReLU6(x + 3) / 6
mish = nn.Mish()                      # Applies mish activation: f(x) = x * tanh(softplus(x))
tanhshrink = nn.Tanhshrink()          # Applies f(x) = x - tanh(x)
threshold = nn.Threshold(0.1, 0)      # Threshold function, values below 0.1 set to 0

['relu', 'prelu', 'selu', 'gelu', 'sigmoid', 'tanh', 'softplus', 'softsign', 'relu6', 'hardsigmoid', 'hardswich', 'mish', 'tanhshrink']
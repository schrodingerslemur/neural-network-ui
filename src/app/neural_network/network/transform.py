import torch

class transform():
    def forward(x, transforms):
        transform_type = transforms[0]

        if transform_type == 'squeeze':
            for dim in transforms[1:]:
                x = torch.squeeze(x, dim=dim)
        else:
            for dim in transforms[1:]:
                x = torch.unsqueeze(x, dim=dim)
        
        return x
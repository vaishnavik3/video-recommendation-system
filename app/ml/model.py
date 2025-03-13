import torch
import torch.nn as nn
import torch.nn.functional as F

class RecSysNN(nn.Module):
    def __init__(self, 
                 user_feat_dim: int = 256,
                 post_feat_dim: int = 512,
                 hidden_dim: int = 1024,
                 dropout: float = 0.3):
        super().__init__()
        
        # User pathway
        self.user_embedding = nn.Embedding(num_embeddings=1000, 
                                        embedding_dim=128)  # For categorical features
        self.user_fc = nn.Sequential(
            nn.Linear(user_feat_dim, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512)
        )
        
        # Post pathway
        self.post_embedding = nn.Embedding(num_embeddings=100, 
                                        embedding_dim=64)  # For categories
        self.post_fc = nn.Sequential(
            nn.Linear(post_feat_dim, 512),
            nn.ReLU(), 
            nn.BatchNorm1d(512)
        )
        
        # Combined network
        self.combined = nn.Sequential(
            nn.Linear(1024, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim//2, 1),
            nn.Sigmoid()
        )
        
    def forward(self, user_features, post_features):
        # Embed categorical features
        user_cat = self.user_embedding(user_features['category'])
        post_cat = self.post_embedding(post_features['category'])
        
        # Process numerical features
        user_num = self.user_fc(user_features['numerical'])
        post_num = self.post_fc(post_features['numerical'])
        
        # Combine features
        combined = torch.cat([
            user_num + user_cat,
            post_num + post_cat
        ], dim=1)
        
        return self.combined(combined)
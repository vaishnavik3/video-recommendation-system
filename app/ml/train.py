import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from torch.nn import BCELoss
from app.core.database import get_db
from app.ml.features import FeatureEngineer
from app.ml.model import RecSysNN

class InteractionDataset(Dataset):
    def __init__(self):
        self.db = next(get_db())
        self.fe = FeatureEngineer()
        self.interactions = self.db.query(Interaction).all()
        
    def __len__(self):
        return len(self.interactions)
    
    def __getitem__(self, idx):
        interaction = self.interactions[idx]
        
        user_feats = self.fe.get_user_features(interaction.user_id, self.db)
        post_feats = self.fe.get_post_features(interaction.post_id, self.db)
        
        # Convert to tensors
        label = torch.tensor([1.0 if interaction.interaction_type in ['like', 'view'] else 0.0])
        
        return {
            'user_features': torch.FloatTensor(user_feats),
            'post_features': torch.FloatTensor(post_feats),
            'label': label
        }

def train_model(epochs=10, lr=0.001):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    model = RecSysNN().to(device)
    optimizer = Adam(model.parameters(), lr=lr)
    criterion = BCELoss()
    
    dataset = InteractionDataset()
    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    
    for epoch in range(epochs):
        for batch in loader:
            optimizer.zero_grad()
            
            outputs = model(
                batch['user_features'].to(device),
                batch['post_features'].to(device)
            )
            
            loss = criterion(outputs, batch['label'].to(device))
            loss.backward()
            optimizer.step()
        
        print(f"Epoch {epoch+1} Loss: {loss.item()}")
    
    # Save trained model
    torch.save(model.state_dict(), "recsys_dnn.pth")
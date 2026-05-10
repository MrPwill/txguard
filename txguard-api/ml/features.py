import math
import numpy as np
import pandas as pd

COUNTRY_COORDS = {
    "US": (37.0902, -95.7129),
    "GB": (55.3781, -3.4360),
    "DE": (51.1657, 10.4515),
    "FR": (46.2276, 2.2137),
    "CA": (56.1304, -106.3468),
    "NG": (9.0820, 8.6753)
}

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

class FeatureEngineer:
    def __init__(self):
        self.account_profiles = {}
        self.global_mean = 0
        self.global_std = 1

    def fit(self, df: pd.DataFrame):
        profiles = df.groupby('account_id').agg(
            mean_amount=('amount', 'mean'),
            std_amount=('amount', 'std'),
            typical_country=('location_country', lambda x: x.mode()[0] if not x.empty else 'US')
        ).to_dict('index')
        
        self.account_profiles = profiles
        self.global_mean = df['amount'].mean()
        self.global_std = df['amount'].std()
        if self.global_std == 0 or pd.isna(self.global_std):
            self.global_std = 1.0

    def transform(self, df: pd.DataFrame):
        """
        Transforms raw transaction data into a feature matrix suitable for ML models.
        """
        X = pd.DataFrame(index=df.index)
        
        def get_z_score(row):
            profile = self.account_profiles.get(row['account_id'])
            if profile and pd.notnull(profile['std_amount']) and profile['std_amount'] > 0:
                return (row['amount'] - profile['mean_amount']) / profile['std_amount']
            return (row['amount'] - self.global_mean) / self.global_std
            
        X['amount_z_score'] = df.apply(get_z_score, axis=1)
        
        # Time of day encoding (cyclical)
        times = pd.to_datetime(df['timestamp'])
        hours = times.dt.hour + times.dt.minute / 60.0
        X['time_sin'] = np.sin(2 * np.pi * hours / 24)
        X['time_cos'] = np.cos(2 * np.pi * hours / 24)
        
        # Geographic Distance
        def get_geo_dist(row):
            profile = self.account_profiles.get(row['account_id'])
            base_country = profile['typical_country'] if profile else row['location_country']
            txn_country = row['location_country']
            
            lat1, lon1 = COUNTRY_COORDS.get(base_country, COUNTRY_COORDS["US"])
            lat2, lon2 = COUNTRY_COORDS.get(txn_country, COUNTRY_COORDS["US"])
            return haversine(lat1, lon1, lat2, lon2)
            
        X['geo_distance_km'] = df.apply(get_geo_dist, axis=1)
        
        # MCC code
        X['mcc_code'] = pd.to_numeric(df['merchant_category_code'], errors='coerce').fillna(5411)
        
        # Velocity Score (count in last 1 hour)
        X['velocity_1h'] = 1.0
        df_temp = df[['account_id', 'timestamp']].copy()
        df_temp['timestamp'] = pd.to_datetime(df_temp['timestamp'])
        
        for account_id, group in df_temp.groupby('account_id'):
            # sort_index is not needed if the original df was somewhat sorted, 
            # but rolling('1h') requires sorted index.
            group_sorted = group.sort_values('timestamp')
            v = group_sorted.set_index('timestamp').rolling('1h').count()
            # Map back to original indices
            X.loc[group_sorted.index, 'velocity_1h'] = v.values.flatten()
        
        # Fill any remaining NaNs
        X = X.fillna(0)
        return X


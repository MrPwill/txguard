import chromadb
import os

# Base path for chromadb persistence
CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/chroma_db")

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_PATH)

def init_db():
    fraud_typologies = client.get_or_create_collection("fraud_typologies")
    aml_regulations = client.get_or_create_collection("aml_regulations")
    past_investigations = client.get_or_create_collection("past_investigations")
    sanctions_data = client.get_or_create_collection("sanctions_data")
    
    # Add some basic synthetic data if empty
    if fraud_typologies.count() == 0:
        fraud_typologies.add(
            documents=[
                "FATF Typology 2023: Structuring involves breaking down large transactions to evade CTR reporting limits of $10,000.",
                "Egmont Case 45: Rapid cross-border movements followed by ATM withdrawals in high-risk jurisdictions often indicates layering.",
                "FinCEN Advisory: Account takeover (ATO) often shows a sudden change in device location, followed by password resets and immediate outbound transfers.",
                "Card testing patterns typically involve multiple small, round-number transactions (e.g., $1.00, $2.00) rapidly attempted at different merchants."
            ],
            ids=["typ_1", "typ_2", "typ_3", "typ_4"]
        )
    
    if aml_regulations.count() == 0:
        aml_regulations.add(
            documents=[
                "Bank Secrecy Act (BSA) CTR requirement: All cash transactions exceeding $10,000 in a single business day must be reported.",
                "FATF Recommendation 10: Financial institutions must undertake customer due diligence (CDD) measures when there are doubts about the veracity or adequacy of previously obtained customer identification data.",
                "EU AMLD6: Obliged entities must apply enhanced customer due diligence (EDD) to business relationships or transactions involving high-risk third countries.",
                "CBN AML/CFT Regulations 2022: Suspicious transactions must be reported to the NFIU within 24 hours of forming the suspicion."
            ],
            ids=["reg_1", "reg_2", "reg_3", "reg_4"]
        )
        
    if sanctions_data.count() == 0:
        sanctions_data.add(
            documents=[
                "OFAC SDN List update: Account holder 'John Doe' (DOB: 1980-01-01) added for terrorism financing.",
                "EU Sanctions: Entity 'Global Trade Corp' added to restricted entities list due to sanctions evasion."
            ],
            ids=["sanc_1", "sanc_2"]
        )
        
    if past_investigations.count() == 0:
        past_investigations.add(
            documents=[
                "Past report 1293: Clear. High velocity was due to subscription billing cycle. Verified."
            ],
            ids=["inv_1"]
        )

# Initialize on import
init_db()

def query_collection(collection_name: str, query: str, n_results: int = 3):
    try:
        collection = client.get_collection(collection_name)
        results = collection.query(query_texts=[query], n_results=n_results)
        # Flatten the list of documents
        if results and 'documents' in results and results['documents']:
            return [doc for sublist in results['documents'] for doc in sublist]
        return []
    except Exception as e:
        print(f"Error querying collection {collection_name}: {e}")
        return []

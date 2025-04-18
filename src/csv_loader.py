import pandas as pd

def load_players(path: str) -> pd.DataFrame:
    """
    Load the roster CSV and normalize column names:
      - 'First Name' → first_name
      - 'Last Name'    → last_name
      - 'Institution'  → school
    """
    df = pd.read_csv(path)

    # Rename to our internal schema
    df = df.rename(columns={
        'First Name': 'first_name',
        'Last Name':  'last_name',
        'Institution':'school'
    })

    # Only keep the columns we need
    return df[['first_name', 'last_name', 'school']]

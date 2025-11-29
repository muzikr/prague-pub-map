import pandas as pd
from ScrapPubs import ScrapPubs

URLS_WHOLE_REPUBLIC = [
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-praha","Prague"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-karlovarsky","Karlovy Vary"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-plzensky","Plzen"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-stredocesky","Středočeský"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-ustecky","Ústecký"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-kralovehradecky","Královéhradecký"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-pardubicky","Pardubický"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-vysocina","Vysočina"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-jihocesky","Jihočeský"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-zlinsky","Zlínský"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-olomoucky","Olomoucký"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-moravskoslezsky","Moravskoslezský"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-jihomoravsky","Jihomoravský"),
     ("https://www.firmy.cz/Restauracni-a-pohostinske-sluzby/Hospody-a-hostince/kraj-liberecky","Liberecký"),
]


def validate_dataframe(url: str, scraper, region : str,f) -> None:
    """
    Validates that the DataFrame contains correct number of pubs.
    """
    df = pd.read_csv(f'pub_urls_{region}.csv',sep=';')
    df = df.drop_duplicates(subset=['url'])
    df_count = df["url"].nunique()
#    print(df["rating"].notna().sum())
#    print(f"Number of pubs in DataFrame: {df_count}")

    list_of_pubs = scraper.get_pubs_urls(url)


    actual_count = len(list_of_pubs)
    print(f"Number of pubs in DataFrame: {df_count}",file = f)

    print(f"Actual number of pubs: {actual_count}",file = f)
    print(f"count of ratings missing: {df['rating'].notna().sum()}",file  = f)

if __name__ == "__main__":
    with open('validator_log.txt', 'w',encoding="utf-8") as f:

        for url, region in URLS_WHOLE_REPUBLIC:
            scraper = ScrapPubs()
            print("======================================================",file=f)
            print(f"Validating region: {region}",file = f)
            validate_dataframe(url, scraper, region,f)
    

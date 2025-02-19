# 10 tasks of Ella

**Overzicht Ella’s 10 taken**

1. Continu energieverbruik monitoren
2. Piekverbruik analyseren en rapporteren
3. Verbruiksprofiel in lijn brengen met type energiecontract
4. Contract duur monitoren
5. Energieverliezen detecteren
6. Monitoren van dagelijkse energieprijzen (adviezen op basis van…)
7. Opvolgen van wetgeving
8. Injectie analyseren
9. Energie budget (opstellen en) bewaken
10. 24/7 bereikbaar

# **Deep dive / Backend per taak**

1. **Continu energieverbruik monitoren**

Van waar komt deze?

- Feature gebaseerd op API Fluvius

Wat moet er weergegeven worden?

- Energieverbruik

—> Year to date of  maandelijks 

**FEATURE:** “Je verbruik is deze maand …… , dit is gelijk aan vorig jaar”

1. **Piekverbruik analyseren en rapporteren**

Van waar komt deze?

- Feature gebaseerd op API Fluvius

Wat moet er weergegeven worden?

- Capaciteitstarief en aansluit-vermogen/toegangsvermogen naast elkaar leggen.

**FEATURE**: 

- “watch out - nieuwe piekconsumptie bereikt!”
- Moment van piekverbruik aantonen en hoeveel keer (historische data)
- ! Alert-email sturen wanneer hier wordt boven gegaan
- Advies geven voor wanneer verbruik te verminderen om piekverbruik te verlagen (Uitleg geven dat minder pieken wil zeggen lagere transport- en capaciteitstarieven of geen extra kosten voor onverwacht hoge pieken)

1. **Verbruiksprofiel in lijn brengen met type energiecontract**

Van waar komt deze?

- Feature die moet ontwikkeld worden door rekening te houden met vaste, variabele of dynamische contracten. Hierbij moeten we kijken naar het verbruik van de KMO (komend uit de API) en de koppeling te leggen met verschillende profielen.

Wat moet er weergegeven worden?

- Huidige type contract (kan gehaald worden uit vragen die gesteld worden bij onboarding) + mogelijks advies

**Feature**: 

- Moet je een maandelijks gemiddeld tarief (variabel, I_Mbelpex) of een dynamish tarief gebruiken?

1. **Contract duur monitoren**

Van waar komt deze?

- Uploaden contract / API ? —> Staat enkel op energie contract

Wat moet er weergegeven worden?

- Contract data

Kijken of er meer of minder dan 100mWh/jaar verbruik is. 

Minder —> U bent een niet gebonden klant, u mag altijd veranderen  

Meer —> Hangt vast aan energiecontract —> Ella moet vragen wanneer het huidige contract eindigt

**Feature**:

- Opgelet: binnen 3 maanden verloopt je contract: Tijd om te kijken voor een nieuw
- U bent een niet gebonden klant (onder 100mWh), verander gerust

1. **Energieverliezen detecteren**

Van waar komt deze?

- Feature gebaseerd op API Fluvius
- Komt van de cosinus phi

Wat moet er weergegeven worden?

- If verliezen, aantonen op dashboard of in maandelijks rapport
- benchmarking doen tussen wat is groen, oranje en rood

**FEATURE**: “doe een energie scan” 

(next: partner waarmee we werken en die komt kijken) 

1. **Monitoren van dagelijkse energieprijzen**

Van waar komt deze?

- API Elia

Wat moet er weergegeven worden?

- “by the way, wist je dat het morgen goedkoop is?”
- Wil je hier meldingen van ontvangen? —> klik aan.

Een ledbar onder de avatar? rood —> duur, oranje —> …, groen —> 

1. **Opvolgen van wetgeving**

Van waar komt deze?

- Eerste maanden eigen input - https://beslissingenvlaamseregering.vlaanderen.be/?themeId=45cfa0c9-82db-4487-8ad4-ca21fa6655ab

Wat moet er weergegeven worden?

- Updates indien relevant

- energie audit - deze is verplicht vanaf een bepaalde drempel (petajoule)
- 

1. **Injectie analyseren**

Van waar komt deze?

- Feature gebaseerd op API Fluvius

Wat moet er weergegeven worden?

- Advies op basis van injectie data
    - Wanneer is er injectie (variabel, dynamisch of vast is hierbij gekoppeld)
    - vb) negatieve energieprijzen → curtailment
    - vb) advies batterij (premium feature)
    
1. **Energie budget (opstellen en) bewaken**

Van waar komt deze?

- Uploaden factuur + API Fluvius

Wat moet er weergegeven worden?

- Verbruik in geld omzetten
    - Vergelijkingen doen met historische data
    
    Wij geven energiebudget (estimate) → en dan maandelijks opvolgen of je op budget zit 
    
    —> hier nog een forecast in geven en inschatten wat de kost voor komend jaar gaat zijn 
    
    —> aanpassingen doen gaat de kost naar beneden helpen, Ella zegt: “Let op mijn taken om jouw energiebudget naar beneden te halen” 
    
    Year energy budget onder avatar in het midden zetten 
    
1. **Ella 24/7 bereikbaar**

Van waar komt deze?

- OpenAI (of dergelijke)

Wat moet er weergegeven worden?

- Chat-functionaliteit met Ella
    - 

**PREMIUM FEATURES**

—> Advies geven naar zonnepanelen of batterij
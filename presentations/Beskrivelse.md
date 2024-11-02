---
marp: true
style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 3rem;

  }

  .center {
    text-align: center;
  }

  .topbar {
  padding-top: 125px;
  }

    .top50 {
  padding-top: 50px;
  }

      .top100 {
  padding-top: 100px;
  }

        .top150 {
  padding-top: 150px;
  }

      header {
        display: grid;
        grid-template-rows: 1fr;
        grid-template-columns: 1fr 1fr;
        grid-gap: 10px;
        box-sizing: border-box;
        justify-content: center;
        width: 100%;
    }

    header img {
        height: 100px;
    }

    footer {
        display: grid;
        grid-template-columns: 1fr max-content;
        align-content: right;
    }
paginate: true

footer: Daníel Örn & Morten Fuglsang 2024 

        
---


![bg](./ressources/Background1.png)

<h1 style="font-size:80px;color:black">Hvad er Q-ETL ?</h1>

---

![bg](./ressources/Slide2.png)

# - Python-baseret ETL værtøj bygget på QGIS.
# - Kræver et basiskendskab til python.
# - Under løbende udvikling.

---

![bg](./ressources/Slide2.png)

# Hvordan fungerer det ?

## - Scripts skrives i python, som afvikles via QGIS' motor.
## - QGIS startes uden brugerflade og afvikler ETL-jobbet.
## - Du kan med QGIS brugerfladen danne de konfigurationer til værktøjer der skal bruges i jobs.

---

![bg](./ressources/Slide2.png)

## Basis eksempel

![height: 500 right:50%](../tutorial//final_code.png)

## Klassisk ETL: Læser data fra service, behandler og skriver data til en database... 
https://github.com/MFuglsang/Q-ETL/wiki/Basic-tutorial

---

![bg](./ressources/Slide2.png)

# Bygget op om en række funktioner:

## - **Input Readers:** Læser data fra filer, databaser, services m.m.
## - **Workers**: laver analyser på data - geometri og atributter.
## - **Integrations**: Udveksling med andet end QGIS - for eksempel Pandas
## - **Output Writers** : Skriver data til alle OGR kompatible kilder.

---

![bg](./ressources/Slide2.png)

# Projekt-status

## - En del værktøjer til vector mappet ind. Flere kommer til løbende.
## - Vi arbejder på understøttelse for rasterdata.
## - Har indført autogenereret dokumentation
https://q-etl-docs.vercel.app/

---

![bg](./ressources/Background1.png)

# Projektet fineds på Github:
https://github.com/MFuglsang/Q-ETL

## Alle er velkomne til at bidrage...


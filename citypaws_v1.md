# Documento dei Requisiti: «CityPaws 時光貓跡» v1.0

## 1. Contesto e Obiettivi del Progetto

**CityPaws** (時光貓跡, "Orme Feline del Tempo") è un'app di **citywalk** (passeggiata urbana) che trasforma l'esplorazione della città in un viaggio di scoperta guidato da **Lucky**, un gattino arancione compagno virtuale. 

Il giocatore cammina nella città reale e incontra punti di interesse (*Anchor*) apparsi sulla mappa in corrispondenza della propria posizione. Raggiungendo un Anchor può fare check-in, scattare foto in realtà aumentata con Lucky come sticker, lasciare un messaggio per i viaggiatori futuri, e sbloccare una **food card** collezionabile legata al luogo visitato. Ogni Anchor custodisce anche un frammento di storia locale che viene rivelato dopo il check-in.

L'esperienza punta a rendere la camminata in città un atto narrativo e collezionistico, combinando localizzazione reale, estetica illustrata a mano e componenti di social lasciati in modo asincrono.

**Obiettivo del progetto**: prototipo universitario/tesi. I dati vengono salvati **solo in locale sul dispositivo**; la funzione "messaggi visibili ai giocatori futuri" sarà simulata tramite un pool di note pre-popolate, mostrate come se fossero state lasciate da altri utenti.

## 2. Personaggi e Identità Visiva

### Personaggi
- **Il giocatore** (protagonista invisibile): rappresentato sulla mappa da un punto blu all'interno di un cerchio di accuratezza GPS.
- **Lucky** (幸運貓): gatto arancione antropomorfo vestito da piccolo cameriere/cuoco con papillon rosso e blocchetto degli ordini ("MEMO"). Funge da guida, narratore e mascotte. Appare come sticker AR nelle foto e come narratore nelle storie sbloccate.

### Palette e stile
- **Sfondo base**: crema/avorio (`#FAF3E0` circa)
- **Accento primario**: rosso mattone (`#B94A3A` circa) — usato per titoli, loghi, bottoni attivi
- **Accento secondario**: verde salvia scuro (`#5A6E4A` circa) — usato per bottoni di conferma, contatori
- **Accento terziario**: marrone caldo — usato per testi e pin Anchor
- **Tono navigazione**: rosa terracotta (`#D18673` circa) — usato per le barre top/bottom nel walking mode
- **Stile grafico**: illustrato a mano, contorni irregolari, estetica "diario di viaggio" o "fumetto acquerellato"
- **Font**: corsivo/hand-written per titoli (logo), sans-serif per testo funzionale

## 3. Asset Visivi (Schermate UI disponibili)

Tutti gli screen sono in formato mobile verticale (rapporto ~9:19.5), esportati da Figma.

| File | Schermata |
|------|-----------|
| `01_Opening_screen.png` | Schermata di avvio con logo CityPaws |
| `calibrating_screen.png` | Calibrazione GPS / homepage iniziale (mappa senza POI) |
| `04_Notification.png` | Notifica di sistema: "New Anchor discovered!" |
| `Navigation_effect.png` | Banner di transizione "Navigating..." |
| `06_saved_to_collection.png` | Popup Anchor con conferma "Anchor is saved to collection!" |
| `07_Walking_mode.png` | Modalità camminata in corso verso l'Anchor |
| `08_near_spot_notification.png` | Banner "You have arrived near the anchor" |
| `09_check_in_page.png` | Popup Anchor con bottone "Check-in" attivo |
| `10_AR_photo_taking_.png` | Fotocamera AR, slot foto vuoto |
| `10_AR_photo_taking_2.png` | Fotocamera AR, sticker Lucky sovrapposto, 1 foto scattata |
| `10_AR_photo_taking_3.png` | Fotocamera AR, 2 foto scattate |
| `AR_photo_taking_4.png` | Fotocamera AR, 3 foto scattate (massimo) |
| `11_leave_a_note.png` | Card con foto scattate + bottone "Leave a note?" |
| `12_Enter_message.png` | Input messaggio con placeholder "How do you feel right now?..." |
| `13_Flipped_history.png` | Retro della card: frammento di storia narrato da Lucky |
| `14_Food_card.png` | Reward: food card collezionata (es. "Corned Beef and Egg Sandwich") |

## 4. Layout delle Schermate Ricorrenti

### Barra superiore (homepage mappa)
- **Alto-sinistra**: pulsante punto interrogativo (`?`) per help/tutorial.
- **Alto-centro**: due contatori in riquadri bordati:
  - Icona lampadina + numero/totale (es. `0/8`): storie sbloccate.
  - Icona cubo/scatola + numero (es. `0`): food card collezionate.
- **Alto-destra**: indicatori di sistema (ora, segnale, batteria).

### Barra laterale sinistra (homepage mappa)
Tre pulsanti tondi sovrapposti verticalmente:
- **Icona griglia con X**: modalità "nascondi POI" (mappa pulita).
- **Icona luna**: modalità notturna della mappa.
- **Icona sole**: modalità diurna della mappa (default).

### Mappa centrale
- Stile Google Maps **retro senza label** (riferimento: https://mapstyle.withgoogle.com/).
- Posizione del giocatore: **punto blu** con cerchio di accuratezza azzurro trasparente.
- Pin Anchor: illustrazione di un personaggio che legge un libro, con icona lucchetto accanto (quando non ancora sbloccato).

### Bussola in basso a destra
Pulsante circolare con icona freccia/bussola: **ricentra la mappa sulla posizione corrente del giocatore**.

### Barra inferiore (5 sezioni principali)
Da sinistra a destra:
1. **Persone/chat**: profilo e amici/community.
2. **Negozio**: shop (icona negozietto).
3. **Mappa** (sezione attiva di default): globo con pin rosso.
4. **Diario**: collezione personale di check-in, note, food card.
5. **Scanner AR**: ingresso rapido alla modalità fotocamera AR.

## 5. Flusso Completo del Gioco

### Step 1 — Avvio dell'app
- Mostra `01_Opening_screen.png` con logo CityPaws e 3 pallini animati (loader).
- Durata: 2-3 secondi.
- **Alla prima apertura**: richiesta di permessi di sistema per **geolocalizzazione** (obbligatoria) e **fotocamera** (richiesta dopo, al primo check-in).

### Step 2 — Homepage / Mappa principale
- Schermata `calibrating_screen.png`: mappa retro centrata sulla posizione GPS del giocatore, barra superiore e inferiore visibili.
- La posizione del giocatore viene aggiornata in tempo reale.
- **Generazione del primo POI**: l'app spawna **un Anchor sulla posizione reale del giocatore** (o a pochi metri, in modo che sia raggiungibile camminando). I POI successivi compaiono a distanze variabili come descritto sotto.

### Step 3 — Comparsa notifica nuovo Anchor
- Quando un nuovo Anchor viene generato nelle vicinanze, compare la notifica `04_Notification.png` in stile push notification dal bordo superiore:
  - Intestazione "CityPaws · now"
  - Titolo: "New Anchor discovered!"
  - Sottotitolo: "This is your first anchor, come check it out!"
- La notifica si auto-nasconde dopo pochi secondi o al tap.

### Step 4 — Tap sull'Anchor (popup info)
- Cliccando sul pin Anchor, si apre un popup (`06_saved_to_collection.png` / `09_check_in_page.png`):
  - **Immagine sfocata con "?"**: teaser del luogo (si rivela solo dopo il check-in).
  - **Bottone stella in alto a destra**: salva l'Anchor nella collezione ("wishlist").
  - **Nome del luogo**: es. "Western Market".
  - **Riga cubetti** (5 caselle): indicatore di **rarità** del luogo (1-5 cubi pieni).
  - **"Lucky says it's safe"**: indicatore di sicurezza del percorso.
  - **Indicatori a destra**:
    - `icona foto + ##%`: percentuale di somiglianza del posto col proprio "gusto" (affinità).
    - `icona freccia + ## km`: distanza in linea d'aria.
    - `icona omino + ## mins`: tempo stimato a piedi.
  - **Bottoni in basso**:
    - **"Maybe later"** (grigio): chiude il popup, l'Anchor resta sulla mappa.
    - **"Let's Walk!"** (marrone scuro): avvia la modalità camminata.
- **Variante dopo salvataggio**: banner superiore "Anchor is saved to collection!" (`06_saved_to_collection.png`).
- **Variante quando si è già nel raggio dell'Anchor**: al posto di "Maybe later/Let's Walk!" appare un singolo bottone **"Check-in"** verde (`09_check_in_page.png`).

### Step 5 — Walking mode
- Dopo il tap su "Let's Walk!":
  - Banner di transizione `Navigation_effect.png` ("Navigating...").
  - Entra in `07_Walking_mode.png`:
    - Barre top e bottom color rosa terracotta.
    - **Top**: messaggio motivazionale / quote breve (personalizzabile in futuro).
    - **Bottom-sinistra**: tempo stimato residuo ("8 mins").
    - **Bottom-destra**: bottone X per annullare la camminata.
    - **Mappa centrale**: linea tratteggiata azzurra che collega la posizione del giocatore all'Anchor di destinazione.

### Step 6 — Arrivo vicino all'Anchor
- Quando il giocatore entra nel **raggio di prossimità** (es. 30-50 metri) dell'Anchor:
  - Cambia il banner superiore in `08_near_spot_notification.png`: "You have arrived near the anchor".
  - Il tempo residuo diventa "1 mins" o meno.

### Step 7 — Check-in
- Tap sul pin Anchor (ora sbloccabile) → popup `09_check_in_page.png` con bottone **"Check-in"** verde attivo.
- Tap su "Check-in" → apertura della fotocamera AR.

### Step 8 — Scatto foto AR (da 1 a 3 foto)
- Schermata `10_AR_photo_taking_.png`:
  - **In alto-sinistra**: bottone "Exit" (verde chiaro).
  - **In alto-destra**: bottone "Complete" (disabilitato finché 0 foto, si attiva dopo la prima foto scattata — `10_AR_photo_taking_2.png`).
  - **Al centro**: anteprima live della fotocamera con cornice bianca irregolare.
  - **Sticker Lucky**: sovrapposto all'anteprima (il giocatore può trascinarlo e ridimensionarlo).
  - **In basso**: bottone di scatto circolare con icona fotocamera.
  - **Sotto il bottone scatto**: 3 slot tratteggiati orizzontali per le anteprime.
- **Regole**:
  - Minimo 1 foto per poter confermare.
  - Massimo 3 foto (gli slot si riempiono progressivamente: `10_AR_photo_taking_2.png` → `10_AR_photo_taking_3.png` → `AR_photo_taking_4.png`).
  - Dopo la terza foto, il bottone scatto si disabilita.
- Tap su **"Complete"**: si passa alla schermata di review.

### Step 9 — Review foto e lascia un messaggio
- Schermata `11_leave_a_note.png`:
  - Stack di card-polaroid con le foto scattate (swipe orizzontale per sfogliarle).
  - Bottone **"Leave a note?"** sotto la card.
- Tap sul bottone → `12_Enter_message.png`:
  - Si apre la tastiera.
  - Campo di input con placeholder: *"How do you feel right now? … Leave a message for future traveller!"*
  - Il giocatore scrive la sua nota e conferma.

### Step 10 — Storia sbloccata (retro della card)
- Dopo la conferma del messaggio, la card si **flippa di 180°** mostrando il retro `13_Flipped_history.png`:
  - Foto storica o illustrazione d'epoca relativa al luogo.
  - Didascalia (es. *"Sheung Wan waterfront-aerial view [1950]"*).
  - **Titolo narrato da Lucky** (in bold): aneddoto breve in prima persona.
  - **Paragrafo**: testo storico/curioso sul luogo (2-4 righe).
  - Bottone **"Read Later"** (verde salvia): chiude il popup e salva la storia nel diario.

### Step 11 — Reward Food Card
- Dopo "Read Later", si mostra la food card `14_Food_card.png`:
  - Sfondo decorativo (piastrelle verdi in stile Hong Kong).
  - **Illustrazione del piatto** al centro (es. panino con corned beef e uovo).
  - **Icona stelline in alto a destra**: rarità della card.
  - Riquadro bianco in basso con:
    - Nome del piatto.
    - Breve descrizione.
    - *"Lucky's favorite"* se applicabile.
    - "Collected at [nome luogo]" + data del check-in.
  - **Bottoni in basso**: "Back" e "Check".
- Tap su **"Check"** → ritorno alla homepage mappa.
- Il contatore food card in alto sulla homepage si incrementa di 1.

## 6. Moduli di Sistema

### A. Modulo Geolocalizzazione
- Lettura della posizione GPS del dispositivo in tempo reale.
- Aggiornamento del punto blu sulla mappa.
- Calcolo della distanza tra giocatore e Anchor attivi.
- Attivazione di eventi a soglia di prossimità (es. "vicino all'Anchor" a 30m, "arrivato" a 10m).
- Gestione permessi (richiesta, rifiuto, fallback).

### B. Modulo Spawn degli Anchor
Regole di generazione dei POI:
- **Primo POI di sempre**: generato esattamente sulla posizione del giocatore (tutorial).
- **POI successivi**: generati a distanza variabile (es. 200m – 2km) dalla posizione del giocatore, in direzione casuale, a intervalli regolari (es. ogni X minuti o ogni tot metri camminati).
- Ogni POI è associato a un **luogo reale** predefinito (pool di luoghi con nome, coordinate, immagine, storia, food card). Per il prototipo, si può usare un JSON locale con 8-10 luoghi mappati.
- I POI già visitati non ricompaiono.

### C. Modulo Anchor Popup
Gestisce la finestra informativa del POI. Stati possibili:
- **Non salvato, lontano**: "Maybe later" / "Let's Walk!"
- **Salvato, lontano**: stesso layout + banner "saved to collection".
- **In walking mode**: popup non visibile, sostituito dal walking overlay.
- **In prossimità**: bottone unico "Check-in" (verde).
- **Già visitato**: popup mostra direttamente la food card e la storia.

### D. Modulo Walking Mode
- Overlay top/bottom rosa terracotta.
- Messaggio motivazionale nel banner superiore (pool di frasi casuali).
- Timer stimato aggiornato in base alla distanza (velocità media a piedi ~ 5 km/h).
- Linea tratteggiata sulla mappa dal giocatore all'Anchor.
- Trigger automatico dello stato "near" quando si entra nel raggio di prossimità.
- Bottone X per annullare e tornare alla mappa.

### E. Modulo Fotocamera AR
- Accesso alla fotocamera del dispositivo.
- **Sticker Lucky** come overlay: draggabile e ridimensionabile sull'anteprima.
- Scatto: salva la foto risultante (foto reale + sticker compositato) nel filesystem locale dell'app.
- Gestione multi-scatto (1-3) con preview slot.
- Salvataggio delle foto associate all'Anchor e alla data di check-in.

### F. Modulo Note e Stories
- Input testuale con carattere massimo (es. 200 caratteri).
- Salvataggio della nota nel database locale associata a: Anchor ID, user ID locale, timestamp.
- **Simulazione note di altri giocatori**: pool di note pre-scritte nel JSON del POI, mostrate come se fossero di utenti diversi quando il giocatore fa check-in o visita l'Anchor in futuro.
- Animazione **flip card 3D** per il passaggio foto → storia.

### G. Modulo Collezione e Reward
- **Food Card**: ogni Anchor ha una food card associata. Dopo il check-in la food card viene aggiunta alla collezione locale.
- **Stories**: ogni Anchor rivela un frammento di storia dopo il check-in. Collezionate nel diario.
- Contatori in homepage aggiornati in tempo reale.
- Sezione "Diario" (barra inferiore) accessibile per rivedere tutte le card e note collezionate.

### H. Persistenza Locale
- Tutte le informazioni vengono salvate **solo sul dispositivo**:
  - Anchor visitati (ID, data check-in)
  - Foto scattate (percorso file locale)
  - Note personali scritte
  - Food card collezionate
  - Storie sbloccate
- Formato suggerito: database locale (SQLite) o JSON strutturato.

## 7. Dati Statici da Pre-popolare

Per il prototipo servono almeno 8-10 **luoghi reali** mappati, ognuno con:
- Nome (es. "Western Market")
- Coordinate GPS (lat, lng)
- Immagine di anteprima (svelata dopo check-in)
- Rarità (1-5 cubetti)
- Percentuale affinità (fittizia o calcolata)
- Frammento di storia (testo + immagine storica + titolo)
- Food card associata (nome piatto, illustrazione, descrizione, rarità)
- Pool di 3-5 note fittizie "da altri giocatori"

Consigliato: organizzare tutti i luoghi in un singolo file `places.json` nel progetto.

## 8. Requisiti Tecnici e Piattaforma

- **Target**: app mobile nativa (iOS e Android).
- **Servizi richiesti**:
  - Geolocalizzazione (GPS)
  - Fotocamera
  - Storage locale
  - Mappa con stile custom (Google Maps SDK con stile retro senza label)
- **Permessi da gestire**: posizione (obbligatorio), fotocamera (al primo check-in), notifiche (opzionale).
- **Modalità offline**: l'app deve funzionare almeno parzialmente senza connessione (la mappa in cache, i dati locali accessibili).

## 9. Funzionalità Future (Fuori MVP)

Elementi visibili nelle schermate ma **non da implementare** nel prototipo di tesi:
- Sezione "Persone/chat" (profilo e amici) nella barra inferiore.
- Sezione "Shop" nella barra inferiore.
- Modalità notturna/diurna della mappa (pulsanti laterali).
- Filtro "nascondi POI" (pulsante griglia).
- Backend per condivisione reale delle note tra utenti.
- Sistema di affinità reale basato sul comportamento.
- Sistema di notifiche push native.

## 10. Note per lo Sviluppo

1. **Focus MVP**: il flusso minimo dimostrabile in tesi è **Avvio → Homepage mappa → Spawn primo Anchor → Tap Anchor → Walking mode → Check-in → Scatto foto AR → Messaggio → Storia → Food card → Ritorno homepage con contatori aggiornati**. Tutto il resto è bonus.

2. **Fedeltà alla UI Figma**: le schermate sono già progettate; la fase di sviluppo consiste nel replicarle fedelmente in termini di layout, colori, padding, dimensioni font.

3. **Test su dispositivo reale**: l'app richiede GPS e fotocamera, quindi non è sufficiente il solo emulatore — serve un test fisico camminando.

4. **Privacy**: tutti i dati restano locali; nella tesi, è utile discutere esplicitamente come questo sia una scelta di design (non solo un limite) per evitare implicazioni GDPR con utenti reali.

5. **Narrativa**: il carattere dell'app è delicato, poetico, nostalgico. Evitare linguaggio da gaming aggressivo; preferire un tono amichevole e narrativo ("Lucky ti porta un pezzo di storia…").

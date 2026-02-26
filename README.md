# Show-Half — Cryptographic Identity Wallet

> A privacy-first, client-side encrypted identity management system that lets users store, control, and selectively share verified identity data using one-time cryptographic keys.

**"Show only half. Keep the rest."**

---

## WARNING — PROPRIETARY SOFTWARE

**Copyright (c) 2026 Pratyush Chaudhari. All Rights Reserved.**

**DO NOT COPY, MODIFY, DISTRIBUTE, OR REPRODUCE ANY PART OF THIS SOFTWARE.**

**DO NOT REVERSE ENGINEER, DECOMPILE, OR CREATE DERIVATIVE WORKS.**

**DO NOT USE THE NAME "SHOW-HALF" OR ANY OF ITS BRANDING WITHOUT WRITTEN PERMISSION.**

**VIOLATORS WILL FACE IMMEDIATE CIVIL AND CRIMINAL LEGAL ACTION** under the following Indian laws:
- The Copyright Act, 1957 — Sections 51, 63, 63B (up to 3 years imprisonment, fines up to Rs. 2,00,000)
- The Patents Act, 1970 — Patent application pending
- The Information Technology Act, 2000 — Sections 43, 65, 66 (compensation up to Rs. 5 crore)
- The Indian Penal Code, 1860
- The Designs Act, 2000
- The Berne Convention and TRIPS Agreement (international)

**Jurisdiction:** Exclusive jurisdiction of the courts in the **State of Maharashtra, India**, under the Government of Maharashtra and the Central Government of India.

For licensing inquiries, contact **Pratyush Chaudhari** directly. Unauthorized use will be prosecuted without prior notice.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Core Concept & Innovation](#core-concept--innovation)
3. [How It Works](#how-it-works)
4. [System Architecture](#system-architecture)
5. [Cryptographic Design](#cryptographic-design)
6. [Key Features](#key-features)
7. [Technology Stack](#technology-stack)
8. [Security Model](#security-model)
9. [Project Structure](#project-structure)
10. [Setup & Deployment](#setup--deployment)
11. [API Reference](#api-reference)
12. [Innovation Claims (Patent-Relevant)](#innovation-claims-patent-relevant)
13. [Glossary](#glossary)

---

## Problem Statement

In today's digital world, identity verification is fundamentally broken:

- **Over-sharing:** When you verify your identity (e.g., for a bank, rental, or job), you hand over your *entire* document — passport, driver's license, Aadhaar, PAN — exposing far more data than necessary.
- **No control:** Once shared, you have zero control over how that data is stored, for how long, or who else sees it.
- **No tamper-proofing:** Scanned documents can be altered. There is no way for a recipient to verify that the data they receive hasn't been tampered with.
- **Centralized risk:** Identity platforms that store user data create honeypot targets for hackers.

**Show-Half solves all four problems.** Show only what's needed. Keep the rest private.

---

## Core Concept & Innovation

Show-Half introduces a novel approach to identity sharing:

### The One-Time Cryptographic Share Key

Instead of sharing a document, Show-Half lets users share a **cryptographically signed, one-time-use key** that contains *only the specific fields* the user selects.

**Example:** A landlord asks to verify your identity. Instead of sending your entire passport:
1. You open Show-Half and select your passport credential.
2. You check *only* "Full Name" and "Date of Birth" — nothing else.
3. Show-Half generates a one-time key: `VID.eyJmaWVsZHMiOnsiZn...`
4. You send that key to the landlord.
5. The landlord pastes it into the public Verify page.
6. The page cryptographically verifies the signature, displays the two fields, and **marks the key as used** — it can never be verified again.

The landlord gets verified data. You keep everything else private. No document was ever shared.

### Key Principles

| Principle | Implementation |
|-----------|---------------|
| **User owns their data** | All identity data is stored in the user's account, never accessible to the platform operator |
| **Selective disclosure** | User chooses exactly which fields to include in each share key |
| **One-time use** | Each key can only be verified once, then it is permanently invalidated |
| **Tamper-proof** | ECDSA digital signatures make it cryptographically impossible to alter shared data |
| **Zero-knowledge verify** | The verifier needs no account and no access to the original document |
| **Client-side crypto** | All key generation, signing, and verification happens in the browser — the server never sees private keys |

---

## How It Works

### Phase 1: Document Import & AI Extraction

```
User uploads document image
        │
        ▼
   ┌─────────────┐
   │  AI Engine   │  (Groq LLaMA 4 Scout - Vision Model)
   │  (Server)    │
   └──────┬──────┘
          │
          ▼
   Structured JSON extracted:
   {
     "documentType": "Passport",
     "fullName": "John Doe",
     "dateOfBirth": "1990-01-15",
     "passportNumber": "AB1234567",
     ...
   }
          │
          ▼
   User reviews & corrects fields
          │
          ▼
   Credential saved to wallet
```

1. User uploads a photo of their identity document (passport, driver's license, national ID, Aadhaar, PAN card).
2. The image is sent to an AI vision model (Meta LLaMA 4 Scout via Groq API) which extracts all visible text fields into structured JSON.
3. The user reviews and can edit any field before saving.
4. Upon saving, Show-Half generates an **ECDSA P-256 key pair**, signs the credential data, and stores the credential with its public key and signature in the user's account.

### Phase 2: Selective Sharing via One-Time Keys

```
User selects credential
        │
        ▼
User picks fields to share:
  ☑ Full Name
  ☑ Date of Birth
  ☐ Passport Number    ← NOT shared
  ☐ Address            ← NOT shared
        │
        ▼
   ┌──────────────────────┐
   │  Key Generation      │
   │                      │
   │  1. Create payload   │
   │     (selected fields │
   │      + metadata)     │
   │                      │
   │  2. Generate new     │
   │     ephemeral ECDSA  │
   │     key pair         │
   │                      │
   │  3. Sign payload     │
   │     with ephemeral   │
   │     private key      │
   │                      │
   │  4. Encode as        │
   │     Base64URL token  │
   │     prefixed "VID."  │
   └──────────┬───────────┘
              │
              ▼
   VID.eyJ2aWQiOiIyIiwia2V5SWQiOiI...
   (One-Time Share Key)
```

The generated key is a self-contained, cryptographically signed token. It includes:
- The selected identity fields (and *only* those fields)
- The ephemeral public key (for verification)
- A unique key ID (for one-time-use enforcement)
- A digital signature (ECDSA P-256 / SHA-256)
- Metadata (issuer credential ID, timestamp, requester name)

### Phase 3: Verification (No Account Required)

```
Verifier receives key
        │
        ▼
   Pastes into Show-Half Verify page
        │
        ▼
   ┌──────────────────────┐
   │  Verification Steps  │
   │                      │
   │  1. Decode Base64URL │
   │  2. Parse JSON       │
   │  3. Check key ID not │
   │     already used     │
   │  4. Extract ephemeral│
   │     public key       │
   │  5. Reconstruct      │
   │     signed payload   │
   │  6. ECDSA Verify     │
   │     signature        │
   │  7. Mark key as used │
   └──────────┬───────────┘
              │
        ┌─────┴─────┐
        │           │
     VALID       INVALID
        │           │
   Show fields   Show error
   + metadata    (tampered /
                  expired /
                  already used)
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                     │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Landing  │  │  Wallet  │  │  Verify  │                 │
│  │  Page     │  │  App     │  │  Page    │                 │
│  │          │  │          │  │  (Public)│                 │
│  └────┬─────┘  └────┬─────┘  └──────────┘                 │
│       │              │                                      │
│       │        ┌─────┴──────┐                              │
│       │        │ Web Crypto │  ← ECDSA P-256               │
│       │        │    API     │  ← All crypto client-side     │
│       │        └────────────┘                              │
│       │                                                     │
└───────┼─────────────────────────────────────────────────────┘
        │              │
        ▼              ▼
┌──────────────┐ ┌──────────────┐
│   Supabase   │ │ Vercel Edge  │
│              │ │   Function   │
│  • Auth      │ │              │
│  • Database  │ │  /api/extract│
│  • RLS       │ │  (Groq Proxy)│
└──────────────┘ └──────┬───────┘
                        │
                        ▼
                 ┌──────────────┐
                 │   Groq API   │
                 │  LLaMA 4     │
                 │  Scout 17B   │
                 └──────────────┘
```

### Component Responsibilities

| Component | Role |
|-----------|------|
| **Landing Page** (`index.html`) | User registration and authentication via Supabase Auth |
| **Wallet App** (`app.html`) | Document upload, AI extraction, credential management, key generation |
| **Verify Page** (`verify.html`) | Public, no-auth key verification with ECDSA signature checking |
| **API Proxy** (`api/extract.js`) | Serverless function that proxies document images to Groq's AI vision model |
| **Supabase Auth** | Email/password authentication with session management |
| **Supabase Database** | Credential storage with Row Level Security (user can only access own data) |
| **Web Crypto API** | Browser-native ECDSA key generation, signing, and verification |

---

## Cryptographic Design

### Algorithms Used

| Purpose | Algorithm | Standard |
|---------|-----------|----------|
| Key Generation | ECDSA P-256 (secp256r1) | NIST FIPS 186-4 |
| Signing | ECDSA with SHA-256 | NIST FIPS 186-4 |
| Verification | ECDSA with SHA-256 | NIST FIPS 186-4 |
| Key Encoding | Raw public key (uncompressed) | SEC 1 v2 |

### Credential Signing Process

When a credential is saved to the wallet:

1. **Key Pair Generation:** A new ECDSA P-256 key pair is generated using the Web Crypto API (`crypto.subtle.generateKey`).
2. **Payload Serialization:** The credential data is serialized to JSON with **deterministic key ordering** (keys sorted alphabetically) to ensure consistent hashing.
3. **Signing:** The serialized payload is signed using the private key with ECDSA-SHA256.
4. **Storage:** The credential data, public key (hex-encoded), and signature (hex-encoded) are stored. The private key is discarded — it is never stored or transmitted.

### Share Key Signing Process

When a one-time share key is generated:

1. **Field Selection:** User selects which fields to include.
2. **Payload Construction:** A JSON object is built containing:
   - `vid`: Version identifier ("2")
   - `keyId`: UUID v4 unique identifier
   - `fields`: Only the selected credential fields
   - `publicKeyHex`: The original credential's public key
   - `requester`: Optional name of the requesting party
   - `credId`: Reference to the source credential
   - `issuedAt`: ISO 8601 timestamp
3. **Ephemeral Key Pair:** A *new, separate* ECDSA P-256 key pair is generated for this specific share operation.
4. **Ephemeral Public Key Embedding:** The ephemeral public key is added to the payload as `ephemeralPubHex`.
5. **Deterministic Serialization:** The payload (including `ephemeralPubHex`, excluding `sig`) is serialized with sorted keys.
6. **Signing:** The serialized payload is signed with the ephemeral private key.
7. **Signature Embedding:** The signature is added to the payload as `sig`.
8. **Encoding:** The complete payload is JSON-serialized, UTF-8 encoded, Base64URL encoded, and prefixed with `VID.`.

### Security Properties

| Property | Guarantee |
|----------|-----------|
| **Integrity** | Any modification to the shared data invalidates the signature |
| **Authenticity** | The signature proves the data was issued by the key holder |
| **Selective Disclosure** | Only user-chosen fields are included; all others are omitted entirely |
| **Non-reusability** | Key IDs are tracked to prevent replay attacks |
| **Forward Secrecy** | Ephemeral keys are used per-share; compromising one key doesn't affect others |
| **Zero-Knowledge** | Verifier learns nothing beyond the disclosed fields |
| **Client-Side Security** | Private keys never leave the browser; the server never sees them |

---

## Key Features

### 1. AI-Powered Document Scanning
- Upload any identity document image (passport, driver's license, national ID, Aadhaar, PAN)
- AI vision model (Meta LLaMA 4 Scout 17B) extracts all text fields automatically
- Supports multiple document types with type-specific field mappings
- All extracted data is editable before saving

### 2. Encrypted Credential Wallet
- Credentials stored in user's authenticated database account
- Row Level Security ensures no user can access another user's data
- Each credential is individually signed with a unique ECDSA key pair
- Signature integrity can be verified at any time

### 3. Selective Disclosure Sharing
- Choose exactly which fields to include in each share
- Optional requester name for audit trail
- Cryptographic signatures ensure tamper-proof delivery
- Each share key is unique and independently signed

### 4. One-Time Verification
- Public verification page — no account required
- Cryptographic ECDSA signature verification in the browser
- Keys expire after first use (one-time enforcement)
- Clear visual feedback: verified fields, timestamp, signature status

### 5. Privacy by Design
- No document images are stored — only extracted text fields
- Private keys are generated and used in the browser, never transmitted
- The server has zero access to cryptographic material
- Minimal data collection: only email for authentication

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Vanilla HTML5, CSS3, JavaScript (ES2017+) | Zero-dependency, works in any modern browser |
| **Cryptography** | Web Crypto API (browser-native) | ECDSA P-256 key generation, signing, verification |
| **AI / Vision** | Groq API + Meta LLaMA 4 Scout 17B 16E Instruct | Document OCR and field extraction |
| **Authentication** | Supabase Auth | Email/password user authentication |
| **Database** | Supabase (PostgreSQL) | Credential storage with Row Level Security |
| **Hosting** | Vercel | Static file hosting + serverless API functions |
| **API Proxy** | Vercel Serverless Functions (Node.js) | Secure Groq API key management |

---

## Security Model

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| **Server compromise** | Server never has access to private keys or raw documents |
| **Man-in-the-middle** | All connections use HTTPS/TLS. Share keys are self-verifying |
| **Data tampering** | ECDSA signatures detect any modification to shared data |
| **Replay attack** | One-time key IDs prevent re-verification of used keys |
| **Unauthorized DB access** | PostgreSQL Row Level Security policies enforce per-user isolation |
| **API key exposure** | Groq API key stored server-side, never exposed to client |

### What the Server Knows vs. Doesn't Know

| Data | Server Access |
|------|--------------|
| User email | Yes (for authentication) |
| Credential text fields | Yes (stored in database) |
| Document images | **No** (processed then discarded) |
| ECDSA private keys | **No** (client-side only) |
| Share key contents | **No** (generated client-side) |
| Verification results | **No** (verified client-side) |

---

## Project Structure

```
show-half/
├── public/                    # Static frontend files
│   ├── index.html             # Landing page + auth (login/signup)
│   ├── app.html               # Main wallet application
│   ├── verify.html            # Public key verification page
│   └── css/
│       └── styles.css         # Shared design system
├── api/
│   └── extract.js             # Vercel serverless function (Groq API proxy)
├── dev_server.py              # Local development server (Python)
├── package.json               # Node.js project metadata
├── vercel.json                # Vercel deployment configuration
└── README.md                  # This file
```

---

## Setup & Deployment

### Prerequisites
- A [Supabase](https://supabase.com) account (free tier)
- A [Groq](https://console.groq.com) API key (free tier)
- A [Vercel](https://vercel.com) account (free tier)
- A [GitHub](https://github.com) account

### 1. Supabase Setup

Create a new Supabase project, then run this SQL in the SQL Editor:

```sql
CREATE TABLE credentials (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  data JSONB NOT NULL,
  public_key_hex TEXT NOT NULL,
  signature_hex TEXT NOT NULL,
  saved_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE credentials ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users read own" ON credentials
  FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users insert own" ON credentials
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users delete own" ON credentials
  FOR DELETE USING (auth.uid() = user_id);
```

### 2. Deploy to Vercel

```bash
git init && git add . && git commit -m "Show-Half v1.0"
git remote add origin https://github.com/USERNAME/show-half.git
git push -u origin main
```

Set environment variable `GROQ_API_KEY` in Vercel dashboard.

### 3. Local Development

```bash
set GROQ_API_KEY=your_key_here
python dev_server.py
# Open http://localhost:3000
```

---

## API Reference

### `POST /api/extract`

Proxies document images to the Groq AI vision model for field extraction.

**Request:**
```json
{
  "mimeType": "image/jpeg",
  "data64": "<base64-encoded image>",
  "prompt": "<extraction instructions>"
}
```

**Response:**
```json
{
  "content": [{ "type": "text", "text": "{\"documentType\":\"Passport\",...}" }]
}
```

---

## Innovation Claims (Patent-Relevant)

### Novel Aspects of Show-Half

1. **Client-Side Cryptographic Identity Tokenization**
   A system for converting identity documents into cryptographically signed, selectively disclosable tokens entirely within the user's browser, without any private key material ever being transmitted to or stored on a server.

2. **One-Time-Use Selective Disclosure Keys**
   A method for generating self-contained, cryptographically signed tokens that include only user-selected identity fields, are bound to a unique identifier, and are enforced as single-use through a verification-time registry.

3. **Ephemeral Key Pair Per-Share Architecture**
   A system where each share operation generates a fresh, independent ECDSA key pair, providing forward secrecy — meaning that compromise of any single share key reveals no information about other shares or the original credential.

4. **Zero-Server-Knowledge Verification**
   A verification protocol where the verifying party can cryptographically confirm the authenticity and integrity of shared identity data without any server involvement, without accessing the original document, and without requiring any account or prior relationship with the identity holder.

5. **AI-Assisted Document Normalization with Human-in-the-Loop**
   A pipeline that combines AI vision models for automated document field extraction with a human review step, allowing the identity holder to correct AI errors before the data is cryptographically committed.

6. **Deterministic Payload Serialization for Signature Stability**
   A method of serializing JSON payloads with deterministic key ordering to ensure that signature verification produces consistent results regardless of internal object property ordering across different JavaScript engines.

### Prior Art Distinction

| Existing Solution | Show-Half Difference |
|-------------------|---------------------|
| **Digital ID cards** (Apple Wallet, DigiLocker) | Show-Half allows *selective field disclosure*, not all-or-nothing sharing |
| **Verifiable Credentials (W3C VC)** | Show-Half is fully client-side, requires no DID infrastructure or blockchain |
| **OAuth / OpenID** | Show-Half shares *verified data*, not just authentication assertions |
| **Document scanning apps** (CamScanner, etc.) | Show-Half adds cryptographic signing, selective sharing, and one-time verification |
| **Blockchain identity** (uPort, Civic) | Show-Half uses no blockchain, no gas fees, no wallet software — just a browser |
| **DigiLocker (India)** | Show-Half provides cryptographic tamper-proofing and selective disclosure; DigiLocker shares full documents |

---

## Glossary

| Term | Definition |
|------|-----------|
| **Credential** | A set of identity fields extracted from a document, stored with its ECDSA public key and signature |
| **Share Key** | A Base64URL-encoded, cryptographically signed token containing selected identity fields (`VID.xxx...`) |
| **Ephemeral Key Pair** | A temporary ECDSA key pair generated for a single share operation and then discarded |
| **Selective Disclosure** | The ability to share only specific fields from a credential while withholding all others |
| **One-Time Use** | A key that can only be verified once; subsequent attempts are rejected |
| **RLS** | Row Level Security — PostgreSQL feature ensuring users can only access their own database rows |
| **ECDSA** | Elliptic Curve Digital Signature Algorithm — the cryptographic algorithm used for signing and verification |
| **P-256** | The NIST-standardized elliptic curve (also called secp256r1) used for key generation |

---

## LICENSE

```
PROPRIETARY SOFTWARE LICENSE

Copyright (c) 2026 Pratyush Chaudhari. All Rights Reserved.
State of Maharashtra, Republic of India.

NO PERMISSION IS GRANTED to copy, reproduce, modify, distribute,
sublicense, sell, reverse engineer, or create derivative works
without prior written consent of Pratyush Chaudhari.

PATENT PENDING under The Patents Act, 1970 (India).

VIOLATION WILL RESULT IN LEGAL ACTION. NO EXCEPTIONS. NO WARNINGS.

Jurisdiction: Courts of Maharashtra, India.

For licensing inquiries contact Pratyush Chaudhari directly.
```

---

*Show-Half -- Show only half. Keep the rest. Your identity, your control.*

*Created by Pratyush Chaudhari. Developed in Maharashtra, India. Protected under Indian and international law.*

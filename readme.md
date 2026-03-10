# 12th Man – Cricket Analytics System

## Team Members

| Name | Sap ID |
|-----|-----|
| Aditya Kathe | 60040230191 |
| Advaith Manoj | 60004230264 |
| Afroz Ansari | 60004230117 |
| Hasan Rampurawala | 60004230162 |

**Guide:**  
Dr. Kiran Bhowmick

Associate Head

---

## Problem Statement

Cricket team selection and match strategy are often influenced by subjective decisions rather than data-driven analysis.  
Existing cricket analytics tools rely mostly on raw statistics such as batting averages, strike rates, and wickets taken, which fail to capture contextual performance factors like venue conditions, opposition strength, and recent player form.

Because of this, teams may face problems such as:

- Biased team selection
- Poor opponent analysis
- Inefficient in-game decisions
- Lack of objective performance evaluation

This project aims to solve these problems using data analytics and machine learning.

## Proposed Solution

**12th Man** is a cricket analytics system that analyzes ball-by-ball cricket data to generate advanced metrics for player evaluation and match strategy.

The system uses metrics such as:

- **Win Probability Added (WPA)** – Measures the impact of each delivery on the probability of winning.
- **Runs Probability Added (RPA)** – Measures runs scored above expected values.

The system provides the following analytics tools:

- Player vs Player (PvP) analysis
- Player vs Team (PvT) analysis
- Player synergy analysis
- Player replacement suggestions
- Best XI team optimizer

These tools help coaches and analysts make **data-driven decisions for team selection and strategy planning**.

---

## Tech Stack / Components Used

### Programming Language
- Python

### Backend
- FastAPI

### Frontend
- Flutter Web

### Data Sources
- Cricsheet dataset: https://cricsheet.org/

---

## Features

- Player analytics
- Player vs Player matchup analysis
- Player vs Team performance analysis
- Batting and bowling synergy detection
- Player replacement recommendation
- Best XI team optimizer
- Team Elo rating system

---

## Project Architecture

The system consists of three major layers:

### 1. Data Processing Layer
- Collects ball-by-ball cricket match data
- Extracts player and match statistics
- Includes venue and weather information

### 2. Analytics Layer
- Computes RPA and WPA metrics
- Generates player vectors
- Stores processed metrics in databases

### 3. Application Layer
Provides APIs for:
- PvP analysis
- PvT analysis
- Synergy analysis
- Best XI optimization
- Player replacement





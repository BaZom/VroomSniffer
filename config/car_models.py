"""
Configuration file for car makes and models.
This module contains the available car makes and their corresponding models.
"""

CAR_MAKES = sorted([
    "Audi", "BMW", "Mercedes-Benz", "Volkswagen", "Opel", "Ford", "Toyota", "Renault", "Peugeot", "Fiat",
    "Hyundai", "Kia", "Mazda", "Seat", "Skoda", "Volvo", "Honda", "Citroën", "Nissan", "Suzuki",
    "Chevrolet", "Dacia", "Jeep", "Mini", "Mitsubishi", "Porsche", "Smart", "Subaru", "Tesla", "Alfa Romeo",
    "Jaguar", "Land Rover", "Lexus", "Saab", "SsangYong", "Daihatsu", "Chrysler", "Cadillac", "Dodge", "Infiniti",
    "Isuzu", "Lancia", "Maserati", "Rover", "Santana", "Daewoo", "Bentley", "Ferrari", "Lamborghini", "Rolls-Royce",
    "Abarth", "Aston Martin", "Bugatti", "Cupra", "DS Automobiles", "Genesis", "Polestar", "RAM", "MG", "BYD"
])

CAR_MODELS = {
    "Audi": ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "Q2", "Q3", "Q5", "Q7", "Q8", "TT", "e-tron", "RS", "S"],
    "BMW": ["1er", "2er", "3er", "4er", "5er", "6er", "7er", "8er", "X1", "X2", "X3", "X4", "X5", "X6", "X7", "Z3", "Z4", "i3", "i4", "i8", "M"],
    "Mercedes-Benz": ["A-Klasse", "B-Klasse", "C-Klasse", "E-Klasse", "S-Klasse", "CLA", "CLS", "GLA", "GLB", "GLC", "GLE", "GLK", "GLS", "G", "SL", "SLC", "SLK", "V-Klasse", "EQC", "AMG"],
    "Volkswagen": ["Golf", "Polo", "Passat", "Tiguan", "Touran", "T-Roc", "T-Cross", "Sharan", "Touareg", "Up!", "Arteon", "Caddy", "ID.3", "ID.4", "ID.5", "ID.7", "Multivan", "Transporter", "Beetle", "Scirocco", "Fox", "Jetta", "Lupo", "Eos", "Corrado", "Bora", "Phaeton"],
    "Opel": ["Adam", "Agila", "Ampera", "Antara", "Astra", "Cascada", "Combo", "Corsa", "Crossland", "Frontera", "Grandland", "Insignia", "Karl", "Meriva", "Mokka", "Omega", "Signum", "Tigra", "Vectra", "Vivaro", "Zafira"],
    "Ford": ["B-MAX", "C-MAX", "EcoSport", "Edge", "Escort", "Fiesta", "Focus", "Fusion", "Galaxy", "Grand C-MAX", "Ka", "Kuga", "Mondeo", "Mustang", "Puma", "Ranger", "S-MAX", "Tourneo", "Transit"],
    "Toyota": ["Auris", "Avensis", "Aygo", "C-HR", "Camry", "Corolla", "GT86", "Hilux", "Land Cruiser", "Prius", "Proace", "RAV4", "Supra", "Urban Cruiser", "Verso", "Yaris"],
    "Renault": ["Captur", "Clio", "Espace", "Grand Scénic", "Kadjar", "Kangoo", "Koleos", "Laguna", "Mégane", "Modus", "Scénic", "Talisman", "Twingo", "Twizy", "ZOE"],
    "Peugeot": ["106", "107", "108", "2008", "206", "207", "208", "3008", "301", "306", "307", "308", "406", "407", "5008", "508", "607", "806", "807", "Expert", "Partner", "RCZ"],
    "Fiat": ["124 Spider", "500", "500C", "500L", "500X", "Bravo", "Doblo", "Fiorino", "Freemont", "Grande Punto", "Idea", "Linea", "Panda", "Punto", "Qubo", "Scudo", "Sedici", "Stilo", "Tipo", "Ulysse"],
    "Hyundai": ["Accent", "Atos", "Bayon", "Elantra", "Getz", "i10", "i20", "i30", "i40", "IONIQ", "ix20", "ix35", "Kona", "Santa Fe", "Tucson", "Veloster"],
    "Kia": ["Carens", "Ceed", "Cerato", "EV6", "Niro", "Optima", "Picanto", "ProCeed", "Rio", "Sorento", "Soul", "Sportage", "Stinger", "Venga", "XCeed"],
    "Mazda": ["2", "3", "5", "6", "CX-3", "CX-30", "CX-5", "CX-7", "CX-9", "MX-5", "RX-8"],
    "Seat": ["Alhambra", "Altea", "Arosa", "Ateca", "Cordoba", "Exeo", "Ibiza", "Leon", "Mii", "Tarraco", "Toledo"],
    "Skoda": ["Citigo", "Enyaq", "Fabia", "Kamiq", "Karoq", "Kodiaq", "Octavia", "Rapid", "Roomster", "Scala", "Superb", "Yeti"],
    "Volvo": ["C30", "C40", "C70", "S40", "S60", "S80", "S90", "V40", "V50", "V60", "V70", "V90", "XC40", "XC60", "XC70", "XC90"],
    "Honda": ["Accord", "Civic", "CR-V", "HR-V", "Insight", "Jazz", "Legend", "Prelude", "S2000"],
    "Citroën": ["Berlingo", "C1", "C2", "C3", "C3 Aircross", "C4", "C4 Cactus", "C4 Picasso", "C5", "C5 Aircross", "C6", "C8", "DS3", "DS4", "DS5", "Jumper", "Jumpy", "Nemo", "Saxo", "Spacetourer", "Xsara"],
    "Nissan": ["350Z", "370Z", "Almera", "Ariya", "Cube", "GT-R", "Juke", "Leaf", "Micra", "Murano", "Navara", "Note", "Pathfinder", "Primera", "Pulsar", "Qashqai", "X-Trail"],
    "Suzuki": ["Alto", "Baleno", "Grand Vitara", "Ignis", "Jimny", "Kizashi", "Liana", "Splash", "Swift", "SX4", "Vitara", "Wagon R"],
    # ...add more makes and models as needed...
}

def get_models_for_make(make):
    """Get available models for a specific car make."""
    return CAR_MODELS.get(make, [])

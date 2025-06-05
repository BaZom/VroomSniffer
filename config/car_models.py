"""
Configuration file for car makes and models.
This module contains the available car makes and their corresponding models.
"""

CAR_MAKES = [
    "BMW",
    "Volkswagen",
    "Audi",
    "Mercedes-Benz"
]

CAR_MODELS = {
    "BMW": ["X1", "X3", "3 Series", "5 Series"],
    "Volkswagen": ["Golf", "Passat", "Tiguan", "Polo"],
    "Audi": ["A3", "A4", "Q3", "Q5"],
    "Mercedes-Benz": ["A-Class", "C-Class", "GLA", "GLB"]
}

def get_models_for_make(make):
    """Get available models for a specific car make."""
    return CAR_MODELS.get(make, [])

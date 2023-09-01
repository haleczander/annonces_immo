class Annonce:
    def __init__(self, reference: str, ville: str, prix: int, surface: int, url: str, description: str, images: list[str], coordonnees: tuple[float, float] = None, disponibilite: str = None, publication: str = None) -> None:
        self.reference = reference
        self.ville = ville
        self.prix = prix
        self.surface = surface
        self.url = url
        self.description = description
        self.images = images
        self.coordonnees = coordonnees
        self.disponibilite = disponibilite
        self.publication = publication
        
    def dict(self) -> dict:
        return {
            self.reference : {
                "ville": self.ville,
                "prix": self.prix,
                "surface": self.surface,
                "url": self.url,
                "description": self.description,
                "images": self.images,
                "coordonnees": self.coordonnees,
                "disponibilite": self.disponibilite,
                "publication": self.publication
            }
        }
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.domain.entities.televisor import Televisor


class TelevisorRepository(ABC):
    """
    Interface del repositorio de televisores (DOMAIN LAYER).
    
    Define el CONTRATO que debe cumplir cualquier implementación
    de persistencia de televisores, sin importar la tecnología específica.
    
    Esta interfaz permite que el dominio no dependa de detalles de
    implementación (JSON, MongoDB, MySQL, etc.)
    """
    
    @abstractmethod
    def save_televisions(self, televisions: List[Televisor], source: str) -> str:
        """
        Guarda una lista de televisores.
        
        Args:
            televisions: Lista de televisores a guardar
            source: Fuente de los datos (alkosto, falabella, etc.)
            
        Returns:
            Identificador del recurso guardado (filepath, id, etc.)
        """
        pass
    
    @abstractmethod
    def load_televisions(self, identifier: str) -> List[Televisor]:
        """
        Carga televisores desde un identificador.
        
        Args:
            identifier: Identificador del recurso (filepath, id, etc.)
            
        Returns:
            Lista de televisores cargados
        """
        pass
    
    @abstractmethod
    def get_latest_file(self, source: str) -> str:
        """
        Obtiene el identificador del archivo/recurso más reciente.
        
        Args:
            source: Fuente de los datos
            
        Returns:
            Identificador del recurso más reciente
        """
        pass
    
    @abstractmethod
    def list_files(self, source: str = None) -> List[str]:
        """
        Lista todos los recursos disponibles.
        
        Args:
            source: Fuente específica (opcional)
            
        Returns:
            Lista de identificadores de recursos
        """
        pass
    
    @abstractmethod
    def get_file_info(self, identifier: str) -> Dict[str, Any]:
        """
        Obtiene información de un recurso específico.
        
        Args:
            identifier: Identificador del recurso
            
        Returns:
            Diccionario con información del recurso
        """
        pass
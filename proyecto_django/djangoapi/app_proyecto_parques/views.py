from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from scripts.crud_zonas import CRUDZonas
from scripts.crud_rutas import CRUDRutas
from scripts.crud_fuentes import CRUDFuentes


class Zonas(APIView):
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crud = CRUDZonas()
    
    def get(self, request):
        try:
            zona_id = request.query_params.get('id')
            if zona_id:
                try:
                    zona_id = int(zona_id)
                except ValueError:
                    return Response(
                        {"ok": False, "message": "El parámetro 'id' debe ser un número entero", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                result = self.crud.selectAsDicts({'id': zona_id})
            else:
                result = self.crud.selectAsDicts()
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en GET: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            if not request.data:
                return Response(
                    {"ok": False, "message": "El body de la petición está vacío", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.insert(request.data)
            
            if result['ok']:
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en POST: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        try:
            if not request.data:
                return Response(
                    {"ok": False, "message": "El body de la petición está vacío", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if 'id' not in request.data:
                return Response(
                    {"ok": False, "message": "El campo 'id' es obligatorio en el body", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.update(request.data)
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en PUT: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            zona_id = request.query_params.get('id') or request.data.get('id')
            
            if not zona_id:
                return Response(
                    {"ok": False, "message": "El parámetro 'id' es obligatorio (query param o body)", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                zona_id = int(zona_id)
            except ValueError:
                return Response(
                    {"ok": False, "message": "El parámetro 'id' debe ser un número entero", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.delete({'id': zona_id})
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en DELETE: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Rutas(APIView):
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crud = CRUDRutas()
    
    def get(self, request):
        try:
            ruta_id = request.query_params.get('id')
            if ruta_id:
                try:
                    ruta_id = int(ruta_id)
                except ValueError:
                    return Response(
                        {"ok": False, "message": "El parámetro 'id' debe ser un número entero", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                result = self.crud.selectAsDicts({'id': ruta_id})
            else:
                result = self.crud.selectAsDicts()
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en GET: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            if not request.data:
                return Response(
                    {"ok": False, "message": "El body de la petición está vacío", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.insert(request.data)
            
            if result['ok']:
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en POST: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        try:
            if not request.data:
                return Response(
                    {"ok": False, "message": "El body de la petición está vacío", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if 'id' not in request.data:
                return Response(
                    {"ok": False, "message": "El campo 'id' es obligatorio en el body", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.update(request.data)
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en PUT: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            ruta_id = request.query_params.get('id') or request.data.get('id')
            
            if not ruta_id:
                return Response(
                    {"ok": False, "message": "El parámetro 'id' es obligatorio (query param o body)", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                ruta_id = int(ruta_id)
            except ValueError:
                return Response(
                    {"ok": False, "message": "El parámetro 'id' debe ser un número entero", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.delete({'id': ruta_id})
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en DELETE: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class Fuentes(APIView):
    permission_classes = [AllowAny]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.crud = CRUDFuentes()
    
    def get(self, request):
        try:
            fuente_id = request.query_params.get('id')
            if fuente_id:
                try:
                    fuente_id = int(fuente_id)
                except ValueError:
                    return Response(
                        {"ok": False, "message": "El parámetro 'id' debe ser un número entero", "data": None},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                result = self.crud.selectAsDicts({'id': fuente_id})
            else:
                result = self.crud.selectAsDicts()
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en GET: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        try:
            if not request.data:
                return Response(
                    {"ok": False, "message": "El body de la petición está vacío", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.insert(request.data)
            
            if result['ok']:
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en POST: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        try:
            if not request.data:
                return Response(
                    {"ok": False, "message": "El body de la petición está vacío", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if 'id' not in request.data:
                return Response(
                    {"ok": False, "message": "El campo 'id' es obligatorio en el body", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.update(request.data)
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en PUT: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            fuente_id = request.query_params.get('id') or request.data.get('id')
            
            if not fuente_id:
                return Response(
                    {"ok": False, "message": "El parámetro 'id' es obligatorio (query param o body)", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                fuente_id = int(fuente_id)
            except ValueError:
                return Response(
                    {"ok": False, "message": "El parámetro 'id' debe ser un número entero", "data": None},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = self.crud.delete({'id': fuente_id})
            
            if result['ok']:
                return Response(result, status=status.HTTP_200_OK)
            return Response(result, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response(
                {"ok": False, "message": f"Error inesperado en DELETE: {str(e)}", "data": None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
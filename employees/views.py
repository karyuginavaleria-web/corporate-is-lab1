import logging

from rest_framework import viewsets

logger = logging.getLogger(__name__)

from .models import Employee, Department
from .serializers import EmployeeSerializer, DepartmentSerializer


class EmployeeViewSet(viewsets.ModelViewSet): 
    queryset = Employee.objects.select_related("department")
    serializer_class = EmployeeSerializer

    def perform_create(self, serializer):
        employee = serializer.save()
        logger.info("Создан сотрудник: %s", employee.full_name)

    def perform_destroy(self, instance):
        logger.warning("Удалён сотрудник: %s", instance.full_name)
        instance.delete()


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
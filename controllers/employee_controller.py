from repositories.employee_repository import EmployeeRepository


class EmployeeController:
    def __init__(self, employee_repository: EmployeeRepository):
        self.employee_repository = employee_repository

    def search_employees(self, params: dict):
        return self.employee_repository.handle_employee_search(params)
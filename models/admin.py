from config import app


class Admin:
    def __init__(self):
        self.managers = []
    
    def update_managers(self):
        cur = app.mysql.connection.cursor()
        cur.execute("SELECT emp_no FROM dept_manager")
        result = cur.fetchall()
        cur.close()
        self.managers = [x[0] for x in result]
    
    def is_manager(self, emp_no):
        return emp_no in self.managers
    
    def remove_manager(self, emp_no):
        if emp_no in self.managers:
            self.managers.remove(emp_no)
            cur = app.mysql.connection.cursor()
            cur.execute("DELETE FROM dept_manager WHERE emp_no = %s", (emp_no,))
            app.mysql.connection.commit()
            cur.close()
            return True
        return False

admin = None
with app.app_context():
    admin = Admin()
    admin.update_managers()

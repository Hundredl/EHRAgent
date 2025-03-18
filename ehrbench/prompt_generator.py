class QueryPromptGenerator:
    """Intelligent Query Prompt Generator"""
    
    OPERATOR_MAP = {
        '>': 'greater than', '<': 'less than', '>=': 'greater than or equal to', '<=': 'less than or equal to',
        '==': 'equal to', '!=': 'not equal to', 'between': 'between', 'in': 'included in'
    }

    def __init__(self):
        self.params = {
            'patient_id': None,         # Patient ID (None means no restriction)
            'date_range': None,         # Date range (tuple or relative description)
            'conditions': [],           # List of query conditions
            'output_format': 'table',   # Output format
            'sort_rules': []            # Sorting rules (field, order)
        }
    
    def set_patient(self, patient_id):
        """Set the patient ID"""
        self.params['patient_id'] = patient_id
    
    def set_date_range(self, start=None, end=None, relative=None):
        """
        Set the date range
        :param start: Absolute start date (YYYY-MM-DD)
        :param end: Absolute end date
        :param relative: Relative time description (e.g., "last three months")
        """
        import datetime
        if relative:
            self.params['date_range'] = ('relative', f"{relative}")
        else:
            if start and type(start) != str:
                start = start.strftime("%Y-%m-%d")
            if end and type(end) != str:
                end = end.strftime("%Y-%m-%d")
            self.params['date_range'] = ('absolute', (start, end))
            
    
    def add_condition(self, field, operator, value):
        """
        Add a query condition
        :param field: Field name
        :param operator: Comparison operator (supports >, <, between, etc.)
        :param value: Comparison value (tuple required for 'between' operator)
        """
        self.params['conditions'].append({
            'field': field,
            'operator': operator,
            'value': value
        })
    
    def set_sorting(self, field, ascending=True):
        """Set sorting rules"""
        self.params['sort_rules'].append((
            field,
            'ascending' if ascending else 'descending'
        ))
    
    def _build_date_description(self):
        """Construct the date range description"""
        if not self.params['date_range']:
            return "no time restrictions"
        
        range_type, value = self.params['date_range']
        if range_type == 'relative':
            return f"within {value}"
        
        start, end = value
        if start and end:
            if start == end:
                return f"on {start}"
            return f"from {start} to {end}"
        if start:
            return f"after {start}"
        if end:
            return f"before {end}"
        return "no time restrictions"
    
    def _build_condition_description(self):
        """Construct the condition description"""
        if not self.params['conditions']:
            return "no specific filtering conditions"
        
        desc = []
        for cond in self.params['conditions']:
            op = self.OPERATOR_MAP.get(cond['operator'], cond['operator'])
            field = f"`{cond['field']}`"
            
            if cond['operator'] == 'between':
                val = f"{cond['value'][0]:.2f} and {cond['value'][1]:.2f}" 
            elif isinstance(cond['value'], list):
                val = ", ".join([str(v) for v in cond['value']])
            else:
                val = str(cond['value']) if type(cond['value']) != float else f"{cond['value']:.2f}"
            
            desc.append(f"{field} {op} {val}")
        return "and meet the following conditions: " + ", ".join(desc)
    
    def generate_prompt(self):
        """Generate a natural language query prompt"""
        # Patient description
        patient_desc = (
            f"patient `{self.params['patient_id']}`" 
            if self.params['patient_id'] else "all patients"
        )
        
        # Sorting description
        sort_desc = ""
        if self.params['sort_rules']:
            sort_rules = [
                f"sorted by `{field} {order}`" 
                for field, order in self.params['sort_rules']
            ]
            sort_desc = ", " + ", ".join(sort_rules)
        
        # Assemble the full prompt
        components = [
            f"Please retrieve data for {patient_desc}",
            self._build_date_description(),
            self._build_condition_description(),
            f"results should be displayed in `{self.params['output_format']}`{sort_desc}"
        ]
        
        # Filter out empty values and join the components
        return "; ".join([c for c in components if c != ""]) + "."

# Example Usage
if __name__ == "__main__":
    # Example 1: Complex query
    q1 = QueryPromptGenerator()
    q1.set_patient("P2024-001")
    q1.set_date_range(start="2023-01-01", end="2023-12-31")
    q1.add_condition("Systolic Blood Pressure", ">", "140 mmHg")
    q1.add_condition("Column", "in", ["Hypertension", "Diabetes"])
    # q1.set_sorting("Visit Date", ascending=False)
    q1.params['output_format'] = "statistical summary include mean, median"
    print("Example 1:\n" + q1.generate_prompt())

    # Example 2: Simple query
    q2 = QueryPromptGenerator()
    q2.set_date_range(relative="2023-10-01")
    q2.add_condition("Age", "between", (30, 50))
    print("\nExample 2:\n" + q2.generate_prompt())
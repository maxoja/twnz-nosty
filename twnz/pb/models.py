class FeatureModel:
    def __init__(self, feature_id, created, updated, expand, collection_id, collection_name, credit_cost_per_week, display_name, enum_name):
        self.feature_id = feature_id
        self.created = created
        self.updated = updated
        self.expand = expand
        self.collection_id = collection_id
        self.collection_name = collection_name
        self.credit_cost_per_week = credit_cost_per_week
        self.display_name = display_name
        self.enum_name = enum_name

    @classmethod
    def from_json(cls, json_data):
        return cls(
            feature_id=json_data['id'],
            created=json_data['created'],
            updated=json_data['updated'],
            expand=json_data['expand'],
            collection_id=json_data['collection_id'],
            collection_name=json_data['collection_name'],
            credit_cost_per_week=json_data['credit_cost_per_week'],
            display_name=json_data['display_name'],
            enum_name=json_data['enum_name']
        )

    def to_json(self):
        # Convert datetime objects to strings
        created_str = self.created.strftime('%Y-%m-%d %H:%M:%S')
        updated_str = self.updated.strftime('%Y-%m-%d %H:%M:%S')

        return {
            'id': self.feature_id,
            'created': created_str,
            'updated': updated_str,
            'expand': self.expand,
            'collection_id': self.collection_id,
            'collection_name': self.collection_name,
            'credit_cost_per_week': self.credit_cost_per_week,
            'display_name': self.display_name,
            'enum_name': self.enum_name
        }


if __name__ == '__main__':
    # Example usage:
    json_data = {
        'id': 'ajkidmhhypurg8s',
        'created': '2023-11-07 12:58:25',
        'updated': '2023-11-09 21:46:21',
        'expand': {},
        'collection_id': 'mh52duw5ximu762',
        'collection_name': 'features',
        'credit_cost_per_week': 2,
        'display_name': 'Nosty Access with Navigation UI',
        'enum_name': 'BASE'
    }

    my_instance = FeatureModel.from_json(json_data)

    # Accessing the attributes
    print(my_instance.feature_id)
    print(my_instance.created)
    print(my_instance.updated)

    # Convert back to JSON
    converted_json = my_instance.to_json()
    print(converted_json)
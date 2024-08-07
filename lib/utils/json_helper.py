#
# Simple JSON helper class
#
class JsonHelper():
    #
    # Safely extracts the attribute, or appends an error if it isn't present
    # and sets the value to the value_if_not_present (defaulted)
    #
    @staticmethod
    def get_attribute(
        json, 
        attribute_name, 
        errors,
        convert_attribute_name_to_lower=True,
        value_if_not_present=None
    ):
        attribute_name_to_use = attribute_name.lower() if convert_attribute_name_to_lower else attribute_name
        value = json.get(attribute_name_to_use, value_if_not_present)

        if value is value_if_not_present:
            errors.append(f"No {attribute_name} specified")

        return value

    
    #
    # Safely extracts the attribute if it exists, or 
    # sets the value to the value_if_not_present (defaulted)
    #
    @staticmethod
    def get_non_mandatory_attribute(
        json, 
        attribute_name, 
        convert_attribute_name_to_lower,
        value_if_not_present
    ):
        attribute_name_to_use = attribute_name.lower() if convert_attribute_name_to_lower else attribute_name

        value = value_if_not_present
        if attribute_name_to_use in json:
            value = json[attribute_name_to_use]
        return value
def validate_allowed_fields(data, allowed_fields, resource_name="resource"):
    unsupported_fields = set(data.keys()) - set(allowed_fields)

    if unsupported_fields:
        raise ValueError(
            f"Invalid fields for {resource_name}: "
            f"{', '.join(unsupported_fields)}. "
            f"Allowed fields: {', '.join(allowed_fields)}"
        )

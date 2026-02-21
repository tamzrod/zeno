# ============================================
# ZENO SCHEMA – MMA Nested Configuration Model
# ============================================
#
# STRUCTURAL VALIDATION ONLY.
# This schema validates configuration SHAPE.
# No value constraints are enforced at this phase.
#
# DESIGN INTENT
# -------------
# - port represents user intent.
#   Export layer converts:
#       port: 502
#   into runtime:
#       listen: ":502"
#
# - Policy is required per memory block (enforced later).
# - Absence of `state_sealing` means state sealing is DISABLED.
# - If `state_sealing` is present:
#       area must be "coil" (validated later).
# - notify ranges may overlap.
# - source_ip must support IPv4, IPv6, and CIDR.
#   (Validation implemented in value phase.)
#
# ============================================

zeno_schema: 1
application: mma
format: nested

root:
  type: object
  properties:

    listeners:
      type: array
      items:
        type: object
        properties:

          id:
            type: string
            # Logical listener identifier.

          port:
            type: integer
            # User-facing TCP port.
            # Export converts:
            #     port: 502
            # into:
            #     listen: ":502"

          memory:
            type: array
            items:
              type: object
              properties:

                unit_id:
                  type: integer
                  # Modbus Unit ID.

                holding_registers:
                  type: object
                  properties:
                    start:
                      type: integer
                      # Zero-based starting address.
                    count:
                      type: integer
                      # Number of registers allocated.

                input_registers:
                  type: object
                  properties:
                    start:
                      type: integer
                    count:
                      type: integer

                coils:
                  type: object
                  properties:
                    start:
                      type: integer
                    count:
                      type: integer

                discrete_inputs:
                  type: object
                  properties:
                    start:
                      type: integer
                    count:
                      type: integer

                policy:
                  type: object
                  properties:

                    rules:
                      type: array
                      items:
                        type: object
                        properties:

                          id:
                            type: string
                            # Rule identifier.

                          source_ip:
                            type: array
                            items:
                              type: string
                            # Each entry must be:
                            # - IPv4 (192.168.1.10)
                            # - IPv6 (2001:db8::1)
                            # - CIDR  (192.168.1.0/24, ::/0)
                            # Value validation implemented later.

                          allow_fc:
                            type: array
                            items:
                              type: integer
                            # MMA Supported Modbus Function Codes:
                            #
                            #   1   Read Coils
                            #   2   Read Discrete Inputs
                            #   3   Read Holding Registers
                            #   4   Read Input Registers
                            #   5   Write Single Coil
                            #   6   Write Single Register
                            #   15  Write Multiple Coils
                            #   16  Write Multiple Registers
                            #
                            # Only these values are valid.
                            #
                            # Example:
                            #   allow_fc: [3, 4, 6, 16]
                            #
                            # Strict enforcement will be implemented
                            # in the value validation phase.


    state_sealing:
      type: object
      properties:

        area:
          type: string
          # If present, must be "coil".
          # If this block is absent entirely,
          # state sealing is disabled.

        start:
          type: integer

        count:
          type: integer


    notify:
      type: object
      properties:

        holding_registers:
          type: array
          items:
            type: object
            properties:
              start:
                type: integer
              count:
                type: integer
              name:
                type: string
                # Logical label for event reporting.

        input_registers:
          type: array
          items:
            type: object
            properties:
              start:
                type: integer
              count:
                type: integer
              name:
                type: string

        coils:
          type: array
          items:
            type: object
            properties:
              start:
                type: integer
              count:
                type: integer
              name:
                type: string

        discrete_inputs:
          type: array
          items:
            type: object
            properties:
              start:
                type: integer
              count:
                type: integer
              name:
                type: string

        influx:
          type: object
          properties:
            url:
              type: string
            token:
              type: string
            org:
              type: string
            bucket:
              type: string
            measurement:
              type: string
              # Optional. Export logic may define default behavior.
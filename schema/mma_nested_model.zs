# ============================================
# ZENO SCHEMA – MMA Nested Configuration Model
# ============================================

zeno_schema: "2.1"
application: "mma"
format: "nested"

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
            unique: sibling

          port:
            type: integer
            unique: sibling

          memory:
            type: array
            items:
              type: object
              properties:

                unit_id:
                  type: integer
                  unique: sibling

                holding_registers:
                  type: object
                  properties:
                    start:
                      type: integer
                    count:
                      type: integer

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
                            unique: sibling

                          source_ip:
                            type: array
                            items:
                              type: string

                          allow_fc:
                            type: array
                            items:
                              type: integer


    state_sealing:
      type: object
      properties:

        area:
          type: string

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
                unique: sibling

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
                unique: sibling

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
                unique: sibling

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
                unique: sibling

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
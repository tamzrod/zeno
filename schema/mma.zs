zeno_schema: 0.1

application:
  name: MMA
  version: 2.x

format:
  type: yaml

meta:
  description: >
    Modbus Memory Appliance configuration schema.
    Nested listener model.
    Zeno uses integer 'port' and maps to runtime 'listen' string.

root:
  type: object
  required: [listeners]
  properties:

    # -------------------------------------------------
    # LISTENERS
    # -------------------------------------------------
    listeners:
      type: list
      min_items: 1
      items:
        type: object
        required: [id, port, memory]
        properties:

          id:
            type: string
            description: Unique listener identifier.

          port:
            type: integer
            minimum: 1
            maximum: 65535
            description: TCP port number. Exported as listen=":<port>".

          memory:
            type: list
            min_items: 1
            items:
              type: object
              required: [unit_id, policy]
              properties:

                unit_id:
                  type: integer
                  minimum: 0
                  maximum: 255
                  description: Modbus unit ID (0–255).

                # -------------------------
                # STATE SEALING
                # -------------------------
                state_sealing:
                  type: object
                  description: >
                    Presence enables sealing.
                    0 = sealed, 1 = unsealed.
                    Only coil area supported in runtime.
                  required: [area, address]
                  properties:
                    area:
                      type: enum
                      values: [coil]
                    address:
                      type: integer
                      minimum: 0

                # -------------------------
                # MEMORY AREAS
                # -------------------------
                coils:
                  $ref: "#/definitions/area"

                discrete_inputs:
                  $ref: "#/definitions/area"

                holding_registers:
                  $ref: "#/definitions/area"

                input_registers:
                  $ref: "#/definitions/area"

                # -------------------------
                # POLICY
                # -------------------------
                policy:
                  type: object
                  required: [rules]
                  properties:
                    rules:
                      type: list
                      min_items: 1
                      items:
                        type: object
                        required: [id, source_ip, allow_fc]
                        properties:

                          id:
                            type: string

                          source_ip:
                            type: list
                            min_items: 1
                            items:
                              type: string
                              format: cidr_or_ip
                              description: >
                                CIDR or bare IP.
                                Bare IP treated as /32 (IPv4) or /128 (IPv6).

                          allow_fc:
                            type: list
                            min_items: 1
                            items:
                              type: integer
                              minimum: 1
                              maximum: 23
                              description: Modbus function code.

                # -------------------------
                # MEMORY-LEVEL NOTIFY
                # -------------------------
                notify:
                  type: object
                  description: >
                    Write-trigger notify rules.
                    Overlapping ranges allowed.
                  properties:
                    coils:
                      $ref: "#/definitions/notify_list"
                    discrete_inputs:
                      $ref: "#/definitions/notify_list"
                    holding_registers:
                      $ref: "#/definitions/notify_list"
                    input_registers:
                      $ref: "#/definitions/notify_list"

    # -------------------------------------------------
    # GLOBAL NOTIFY OUTPUT
    # -------------------------------------------------
    notify:
      type: object
      description: Optional notify output adapters.
      properties:
        influx:
          type: object
          required: [url, token, org, bucket]
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
              description: Optional measurement name.

definitions:

  area:
    type: object
    required: [start, count]
    properties:
      start:
        type: integer
        minimum: 0
      count:
        type: integer
        minimum: 1

  notify_list:
    type: list
    min_items: 1
    items:
      type: object
      required: [start, count]
      properties:
        start:
          type: integer
          minimum: 0
        count:
          type: integer
          minimum: 1
        name:
          type: string
          description: Optional logical name of notify block.
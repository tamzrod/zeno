zeno_schema: "2.0"
application: "ZENO"
format: "yaml"

root:
  type: object
  properties:
    server:
      type: object
      properties:
        port:
          type: integer
          default: 8080
        host:
          type: string
          default: "localhost"
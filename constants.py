# RabbitMQ Queues
BASKET_QUEUE_NAME = "Basket"
CATALOG_QUEUE_NAME = "Catalog"
PAYMENT_QUEUE_NAME = "Payment"
ORDERING_QUEUE_NAME = "Ordering"

# Docker Containers Identifiers
ORDERING_SERVICE = "eshop/ordering.api:linux-latest"
ORDERING_BACKGROUND_TASK_SERVICE = "eshop/ordering.backgroundtasks:linux-latest"
SIGNALR_HUB_SERVICE = "eshop/ordering.signalrhub:linux-latest"
BASKET_SERVICE = "eshop/basket.api:linux-latest"
CATALOG_SERVICE = "eshop/catalog.api:linux-latest"
PAYMENT_SERVICE = "eshop/payment.api:linux-latest"
IDENTITY_SERVICE_ID = "bcb150ac21d645d8979fbcb7c9e6891c6536506617f94faad5af05e45ee66886"

# Statues
SUBMITTED_STATUS = 1
AWAITING_VALIDATION_STATUS = 2
STOCK_CONFIRMED_STATUS = 3
PAID_STATUS = 4
SHIPPED_STATUS = 5
CANCELED_STATUS = 6

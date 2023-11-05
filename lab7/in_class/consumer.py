import sys
import json
import pika
import threading

class Consumer():

    def __init__(self, id, host, queue_name, file):
        self.id = id
        self.host = host
        self.queue_name = queue_name
        self.file = file

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self.channel = self.connection.channel()
        self.lock = threading.Lock()

        self.channel.queue_declare(queue=queue_name)

    def on_message_callback(self, ch, method, properties, body):
        print(f" [x] Consumer {self.id} received {json.loads(body)}")
        with self.lock:
            self.file.write(body)
    
    def consume_message(self):
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_message_callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()
    
    def start_consume(self):
        try:
            self.consume_message()
        except KeyboardInterrupt:
            print("Exiting...")
            sys.exit(0)

if __name__=="__main__":
    # TODO: Fix json format 

    number_of_consumers = 5

    with open("data.json", "wb") as file:
        consumers = [Consumer(id+1, "localhost", "scraper_queue", file) for id in range(number_of_consumers)]
        threads = [threading.Thread(target=consumer.start_consume, args=()) for consumer in consumers]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()


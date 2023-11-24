class Node:

    def __init__(self, uuid, is_leader, followers = None):
        self.uuid = uuid 
        self.is_leader = is_leader
        self.followers = followers if self.is_leader else None

    def string(self):
        print(f"Node::{self.uuid} is leader: {self.is_leader}")
        if self.is_leader:
            print(f"Followers: {self.followers}")

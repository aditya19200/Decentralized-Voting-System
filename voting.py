import hashlib
import json
from typing import List, Dict
from datetime import datetime, timedelta

class BlockchainVotingSystem:
    def __init__(self, election_name: str, candidates: List[str], voting_duration_days: int = 7):
        """
        Initialize the blockchain voting system
        
        :param election_name: Name of the election
        :param candidates: List of candidates
        :param voting_duration_days: Duration of the election
        """
        self.chain: List[Dict] = []
        self.pending_votes: List[Dict] = []
        self.candidates = candidates
        self.election_name = election_name
        
        # For testing purposes, allow manual override of election time
        self.election_start = datetime.now()
        self.election_end = datetime.now() + timedelta(days=voting_duration_days)
        
        # Voter registry to prevent double voting
        self.voted_voters: set = set()
        
        # Create genesis block
        self.create_block(previous_hash="0", proof=100)

    def create_block(self, proof: int, previous_hash: str) -> Dict:
        """
        Create a new block in the blockchain
        
        :param proof: Proof of work
        :param previous_hash: Hash of the previous block
        :return: New block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now().isoformat(),
            'votes': self.pending_votes.copy(),  # Create a copy of pending votes
            'proof': proof,
            'previous_hash': previous_hash,
            'election_name': self.election_name
        }
        
        # Reset pending votes
        self.pending_votes = []
        
        # Add block to the chain
        self.chain.append(block)
        return block

    def cast_vote(self, voter_id: str, candidate: str) -> Dict:
        """
        Cast a vote in the election
        
        :param voter_id: Unique identifier for the voter
        :param candidate: Candidate being voted for
        :return: Vote details
        """
        # Validate candidate
        if candidate not in self.candidates:
            raise ValueError(f"Invalid candidate. Choose from: {self.candidates}")
        
        # Prevent double voting
        if voter_id in self.voted_voters:
            raise ValueError("This voter has already cast a vote")
        
        # Create vote
        vote = {
            'voter_id': self.hash_voter_id(voter_id),
            'candidate': candidate,
            'timestamp': datetime.now().isoformat()
        }
        
        # Record vote and mark voter
        self.pending_votes.append(vote)
        self.voted_voters.add(voter_id)
        
        return vote

    @staticmethod
    def hash_voter_id(voter_id: str) -> str:
        """
        Hash voter ID to maintain anonymity
        
        :param voter_id: Original voter ID
        :return: Hashed voter ID
        """
        return hashlib.sha256(voter_id.encode()).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple Proof of Work algorithm
        
        :param last_proof: Previous proof
        :return: New proof
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validate the proof of work
        
        :param last_proof: Previous proof
        :param proof: Current proof
        :return: Whether proof is valid
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def get_election_results(self, force_close: bool = False) -> Dict:
        """
        Tally and return election results
        
        :param force_close: Override election time check for testing
        :return: Dictionary of vote counts
        """
        # Count votes across all blocks
        vote_counts = {candidate: 0 for candidate in self.candidates}
        
        for block in self.chain:
            for vote in block.get('votes', []):
                vote_counts[vote['candidate']] += 1
        
        return {
            'election_name': self.election_name,
            'total_votes': sum(vote_counts.values()),
            'results': vote_counts,
            'winner': max(vote_counts, key=vote_counts.get)
        }

def main():
    # Create a voting system for a student council election
    candidates = ['Alice', 'Bob', 'Charlie']
    voting_system = BlockchainVotingSystem(
        election_name="Student Council Election", 
        candidates=candidates,
        voting_duration_days=7
    )

    # Simulate votes
    sample_voters = [
        ('voter1@school.edu', 'Alice'),
        ('voter2@school.edu', 'Bob'),
        ('voter3@school.edu', 'Charlie'),
        ('voter4@school.edu', 'Alice'),
        ('voter5@school.edu', 'Bob')
    ]

    print("🗳️ Casting Votes:")
    for voter_id, candidate in sample_voters:
        try:
            vote = voting_system.cast_vote(voter_id, candidate)
            print(f"Vote cast: {vote}")
        except ValueError as e:
            print(f"Vote error: {e}")

    # Mine a block
    last_block = voting_system.chain[-1]
    proof = voting_system.proof_of_work(last_block['proof'])
    previous_hash = voting_system.hash_voter_id(str(last_block))
    voting_system.create_block(proof, previous_hash)

    # Simulate election end and get results
    print("\n🏆 Election Results:")
    results = voting_system.get_election_results(force_close=True)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()



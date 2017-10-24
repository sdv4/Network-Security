
import java.util.concurrent.locks.*;

/**
 * TxQueue Class
 * 
 * TxQueue implements a queue of nodes (contaning segment) using a link list. The nodes are stored in increasing order of segment sequence number
 * A node item is inserted into the queue based on segment sequence number, while items are ALWAYS removed from the 'head' of the queue. Neverteless, for the sender, a new node is always added at the end. The implementation is generic to incorporate receiver side queue.
 * The next segment to be removed is at the 'head'.
 * 
 * This is a blocking implementation:
 * The queue has a capacity. A call to add() when the queue is full
 * blocks the calling process until space becomes available by calling remove().
 * A call to remove() when the queue is empty will block the calling process until
 * a segment is added to the queue using add(). 
 * 
 * @author      Majid Ghaderi
 * @author      Cyriac James
 * @version     3.1, Jan 01, 2017
 *
 */
public class TxQueue {
	
	// used for mutual exclusion, can be unlocked only by the locking process
	private final ReentrantLock mutex;

	// conditions used for capacity management
	private final Condition notFull;
	private final Condition notEmpty;
	
	// queue ADT variables to implement a segment node List
	private TxQueueNode head = null;
	private TxQueueNode tail = null;
	private int count = 0;
	private int length = 0;
	
    	/**
     	* Constructor 
     	* 
     	* Creates a queue of given capacity
     	* 
     	* @param capacity	The capacity of the queue
     	*/
	public TxQueue(int capacity) {
		mutex = new ReentrantLock();
		
		notFull = mutex.newCondition();
		notEmpty = mutex.newCondition();
		
		length = capacity;
	}
	
	
    	/**
	* Returns queue node which contains segment of given sequence number
     	*  
     	* 
     	* @return The TxQueueNode
	*	If no match is found, returns returns null
     	*/
	public TxQueueNode getNode(int seq) {
		// prevents others from accessing queue
		mutex.lock();
		
		try {
			TxQueueNode temp = null;
			TxQueueNode current = head;
			for (int i = 0; i < count; i++) {
				if(current.seg.getSeqNum() == seq)
				{
					temp = current;
					break;
				}
				else
				{
					current = current.next;
					continue;
				}
			}
			return temp;
		}
		finally {
			// release the lock
			mutex.unlock();
		}
	}



	/**
        * Returns segment of given sequence number from the queue
     	*  
     	* 
     	* @return The segment
        *       If no match is found, returns returns null
     	*/
	public Segment getSegment(int seq) {
                // prevents others from accessing queue
                mutex.lock();

                try {
                        TxQueueNode tmp = null;
                        TxQueueNode current = head;
                        for (int i = 0; i < count; i++) {
                                if(current.seg.getSeqNum() == seq)
                                {
                                        tmp = current;
                                        break;
                                }
                                else
                                {
                                        current = current.next;
                                        continue;
                                }
                        }
                        if(tmp != null)
				return tmp.seg;
			else
				return null;
                }
                finally {
                        // release the lock
                        mutex.unlock();
                }
        }

	/**
     	* Returns the node at the head of the queue, but does not remove it.  
     	* 
     	* @return  The TxQueueNode
     	*                  If queue is empty, returns null
     	*/
        public TxQueueNode getHeadNode() {
                // prevents others from accessing queue
                mutex.lock();

                try {
                        TxQueueNode node = null;
                        if (count != 0)
                                node = head;

                        return node;
                }
                finally {
                        // release the lock
                        mutex.unlock();
                }
        }

    	/**
     	* Returns the segment at the 'head' of the queue, but does not remove it.  
     	* 
     	* @return	The 	Segment
     	* 			If queue is empty, returns null
     	*/
	public Segment getHeadSegment() {
		// prevents others from accessing queue
		mutex.lock();
		
		try {
			Segment seg = null;
			if (count != 0)
				seg = head.seg;
			
			return seg;
		}
		finally {
			// release the lock
			mutex.unlock();
		}
	}

	
    	/**
     	* Adds a segment to the queue based on the sequence number if there is any space available,
     	* otherwise, the calling process is blokced until space becomes available.
     	* The segments are arranged in the TxQueue in increasing order of sequence numbers
     	* 
     	* @param seg	The segment to be added to the queue
     	* @throws InterruptedException in case the thread excecution is interrupted
     	*/
	public void add(Segment seg) throws InterruptedException {
		// prevents others from accessing queue
		mutex.lock();
		
		try {
			// wait for space to become available in queue
			if (count == length)
				notFull.await();
			
			// add the segment at the tail of the queue
			if(count == 0) // queue is empty
			{
				TxQueueNode node = new TxQueueNode(seg);
				head = node;
				tail = node;
				head.next = null;
				tail.next = null;
			}
			else // queue is non-empty
			{
                                TxQueueNode node = new TxQueueNode(seg);
				TxQueueNode tmp = head;
                        	TxQueueNode prev = tmp;
				boolean added = false;
                        	while(tmp != null) // traverse through the queue
                        	{
                                	if(tmp.seg.getSeqNum() > node.seg.getSeqNum())
                                	{
                                        	if(head == tmp) 
                                                	head = node;
                                        	else
                                                	prev.next = node;
                                        	node.next = tmp;
						added = true;
                                        	break;
                                	}
                                	else
                                	{
                                        	prev = tmp;
                                        	tmp = tmp.next;
                                	}
				}
                        	if(!added)
				{
					prev.next = node;
					node.next = null;
					tail = node;
				}
			}
				
			count++;
			
			// queue is not empty anymore
			notEmpty.signal();
		}
		finally {
			// release the lock
			mutex.unlock();
		}
	}

	
    	/**
     	* Removes and returns the segment at the 'head' of the queue if the queue is not empty,
     	* otheriwse, will block the calling process until a segment becomes available. 
     	* 
     	* @return 	The segment at the head of the queue
     	* @throws InterruptedException in case the thread excecution is interrupted
     	*/
	public Segment remove() throws InterruptedException {
		// prevents others from accessing queue
		mutex.lock();

		
		try {
			// wait for items to be added to queue
			if (count == 0)
				notEmpty.await();
			
			// remove the head of the queue and return it
			TxQueueNode node = head;
			if(head == tail)
			{
				head = null;
				tail = null;
			}
			else
			{
				head = head.next;
			}
			count--;
			
			// queue is not full anymore
			notFull.signal();
			
			return node.seg;
		}
		finally {
			// release the lock
			mutex.unlock();
		}
	}

    	/**
     	* Returns the number of nodes (or segments) in the queue.
     	* 
     	* @return 	The number of nodes (or segments) in the queue
     	*/
	public int size() {
		// prevents others from accessing queue
		mutex.lock();
		
		try {
			// size = capacity - occupied
			return count;
		}
		finally {
			// release the lock
			mutex.unlock();
		}
	}

	
    	/**
    	 * Checks if the queue is empty.
     	* 
     	* @return 	true if the queue is empty, false otherwise
     	*/
	public boolean isEmpty() {
		// prevents others from accessing queue
		mutex.lock();
		
		try {
			return (count == 0);
		}
		finally {
			// release the lock
			mutex.unlock();
		}
	}

	
    	/**
     	* Checks if the queue is full.
     	* 
     	* @return 	true if the queue is full, false otherwise
     	*/
	public boolean isFull() {
		// prevents others from accessing queue
		mutex.lock();
		
		try {
			return (count == length);
		}
		finally {
			// release the lock
			mutex.unlock();
		}
	}
}



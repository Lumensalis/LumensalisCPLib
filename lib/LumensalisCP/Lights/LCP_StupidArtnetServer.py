"""(Very) Simple Implementation of Artnet.

Python Version: 3.6
Source: http://artisticlicence.com/WebSiteMaster/User%20Guides/art-net.pdf


NOTES


- For simplicity: NET and SUBNET not used by default but optional

"""
"""Provides common functions byte objects."""


### HACK
## this is pulled in directly to work around issues related 
## to importing socket instead of socketpool

def shift_this(number, high_first=True):
    """Utility method: extracts MSB and LSB from number.

    Args:
    number - number to shift
    high_first - MSB or LSB first (true / false)

    Returns:
    (high, low) - tuple with shifted values

    """
    low = (number & 0xFF)
    high = ((number >> 8) & 0xFF)
    if high_first:
        return((high, low))
    return((low, high))


def clamp(number, min_val, max_val):
    """Utility method: sets number in defined range.

    Args:
    number - number to use
    range_min - lowest possible number
    range_max - highest possible number

    Returns:
    number - number in correct range
    """
    return max(min_val, min(number, max_val))


def set_even(number):
    """Utility method: ensures number is even by adding.

    Args:
    number - number to make even

    Returns:
    number - even number
    """
    if number % 2 != 0:
        number += 1
    return number


def put_in_range(number, range_min, range_max, make_even=True):
    """Utility method: sets number in defined range.
    DEPRECATED: this will be removed from the library

    Args:
    number - number to use
    range_min - lowest possible number
    range_max - highest possible number
    make_even - should number be made even

    Returns:
    number - number in correct range

    """
    number = clamp(number, range_min, range_max)
    if make_even:
        number = set_even(number)
    return number


def make_address_mask(universe, sub=0, net=0, is_simplified=True):
    """Returns the address bytes for a given universe, subnet and net.

    Args:
    universe - Universe to listen
    sub - Subnet to listen
    net - Net to listen
    is_simplified - Whether to use nets and subnet or universe only,
    see User Guide page 5 (Universe Addressing)

    Returns:
    bytes - byte mask for given address

    """
    address_mask = bytearray()

    if is_simplified:
        # Ensure data is in right range
        universe = clamp(universe, 0, 32767)

        # Make mask
        msb, lsb = shift_this(universe)  # convert to MSB / LSB
        address_mask.append(lsb)
        address_mask.append(msb)
    else:
        # Ensure data is in right range
        universe = clamp(universe, 0, 15)
        sub = clamp(sub, 0, 15)
        net = clamp(net, 0, 127)

        # Make mask
        address_mask.append(sub << 4 | universe)
        address_mask.append(net & 0xFF)

    return address_mask


import socketpool
globals()['socket'] = socketpool
#from stupidArtnet.ArtnetUtils import make_address_mask

from socketpool import SocketPool
import socketpool as socket
import wifi

import asyncio
#from asyncio import Server

class StupidArtnetASIOServer():
    """(Very) simple implementation of an Artnet Server."""

    socket_server = None
    ARTDMX_HEADER = b'Art-Net\x00\x00P\x00\x0e'
    listeners = []

    def __init__(self, pool:socketpool.SocketPool, port=6454):
        """Initializes Art-Net server."""
        self.port = port  # Use provided port or default
        # By default, the server uses port 6454, no need to specify it.
        # If you need to change the Art-Net port, ensure the port is within the valid range for UDP ports (1024-65535).
        # Be sure that no other application is using the selected port on your network.
        
        # server active flag
        self.listen = True


        #self.server_thread = _thread.start_new_thread(self.__init_socket, ())
        self.__init_socket(pool)
        
    def __init_socket(self, pool:socketpool.SocketPool ):
        """Initializes server socket."""
        # Bind to UDP on the correct PORT
        self.pool:socketpool.SocketPool = pool
        self.socket_server = pool.socket(SocketPool.AF_INET, SocketPool.SOCK_DGRAM)
        self.socket_server.setsockopt(
            SocketPool.SOL_SOCKET, SocketPool.SO_REUSEADDR, 1)
        self.socket_server.settimeout(0)
        self.socket_server.bind(('', self.port))  # Listen on any valid IP
        
        
    async def _listenLoop(self):
        loop = asyncio.get_event_loop()
        data = bytearray(1024)
        while self.listen:
            await asyncio.sleep(0.005)
            try:
                dataLen, unused_address = self.socket_server.recvfrom_into(data)
            except Exception as inst:
                if isinstance( inst, OSError ) and inst.errno == 11: continue
                print( f"dmx read exception : {inst}")
                continue
            if dataLen == 0:
                continue
            
            #data, unused_address = await loop.sock_recv( self.socket_server, 1024)
            # only dealing with Art-Net DMX
            #print( f"received [{dataLen}]:{ data}")
            if self.validate_header(data):

                # check if this address is in any registered listener
                for listener in self.listeners:

                    # is it the address we are listening to
                    if listener['address_mask'] == data[14:16]:

                        # check if the packet we've received is old
                        new_seq = data[12]
                        old_seq = listener['sequence']
                        # if there's a >50% packet loss it's not our problem
                        if new_seq == 0x00 or new_seq > old_seq or old_seq - new_seq > 0x80:
                            listener['sequence'] = new_seq

                            listener['buffer'] = list(data)[18:]

                            # check for registered callbacks
                            callback = listener['callback']
                            if callback is not None:
                                if 1:
                                    addr_mask = listener['address_mask']
                                    addr = int.from_bytes(addr_mask, 'little')
                                    callback(listener['buffer'], addr)
                                else:
                                    # choose the correct callback call based
                                    # on the number of the function's parameters
                                    try:
                                        from inspect import signature
                                        params = signature(callback).parameters
                                        params_len = len(params)
                                    except ImportError:
                                        params_len = 2
                                    
                                    if params_len == 1:
                                        callback(listener['buffer'])
                                    elif params_len == 2:
                                        addr_mask = listener['address_mask']
                                        addr = int.from_bytes(addr_mask, 'little')
                                        callback(listener['buffer'], addr)

    def __del__(self):
        """Graceful shutdown."""
        self.listeners.clear()
        self.close()

    def __str__(self):
        """Printable object state."""
        state = "===================================\n"
        state += "Stupid Artnet Listening\n"
        return state

    def register_listener(self, universe=0, sub=0, net=0,
                          is_simplified=True, callback_function=None):
        """Adds a listener to an Art-Net Universe.

        Args:
        universe - Universe to listen
        sub - Subnet to listen
        net - Net to listen
        is_simplified - Whether to use nets and subnet or universe only,
        see User Guide page 5 (Universe Addressing)
        callback_function - Function to call when new packet is received

        Returns:
        id - id of listener, used to delete listener if required
        """
        listener_id = len(self.listeners)
        new_listener = {
            'id': listener_id,
            'simplified': is_simplified,
            'address_mask': make_address_mask(universe, sub, net, is_simplified),
            'callback': callback_function,
            'buffer': [],
            'sequence': 0
        }

        self.listeners.append(new_listener)

        return listener_id

    def delete_listener(self, listener_id):
        """Deletes a registered listener.

        Args:
        listener_id - Id of listener to delete

        Returns:
        None
        """
        self.listeners = [
            i for i in self.listeners if not i['id'] == listener_id]

    def delete_all_listener(self):
        """Deletes all registered listeners.

        Returns:
        None
        """
        self.listeners = []

    def see_buffer(self, listener_id):
        """Show buffer values."""
        for listener in self.listeners:
            if listener.get('id') == listener_id:
                return listener.get('buffer')

        return "Listener not found"

    def get_buffer(self, listener_id):
        """Return buffer values."""
        for listener in self.listeners:
            if listener.get('id') == listener_id:
                return listener.get('buffer')
        print("Buffer object not found")
        return []

    def clear_buffer(self, listener_id):
        """Clear buffer in listener."""
        for listener in self.listeners:
            if listener.get('id') == listener_id:
                listener['buffer'] = []

    def set_callback(self, listener_id, callback_function):
        """Add / change callback to a given listener."""
        for listener in self.listeners:
            if listener.get('id') == listener_id:
                listener['callback'] = callback_function

    def set_address_filter(self, listener_id, universe, sub=0, net=0,
                           is_simplified=True):
        """Add / change filter to existing listener."""
        # make mask bytes
        address_mask = make_address_mask(
            universe, sub, net, is_simplified)

        # find listener
        for listener in self.listeners:
            if listener.get('id') == listener_id:
                listener['simplified'] = is_simplified
                listener['address_mask'] = address_mask
                listener['buffer'] = []

    def close(self):
        """Close UDP socket."""
        self.listen = False         # Set flag, so thread will exit

    @staticmethod
    def validate_header(header):
        """Validates packet header as Art-Net packet.

        - The packet header spells Art-Net
        - The definition is for DMX Artnet (OPCode 0x50)
        - The protocol version is 15

        Args:
        header - Packet header as bytearray

        Returns:
        boolean - comparison value

        """
        return header[:12] == StupidArtnetASIOServer.ARTDMX_HEADER


def test_callback(data):
    """Test function, receives data from server callback."""
    print('Received new data \n', data)


if __name__ == '__main__':

    import time

    print("===================================")
    print("Namespace run")

    # Art-Net 4 definition specifies nets and subnets
    # Please see README and Art-Net user guide for details
    # Here we use the simplified default
    UNIVERSE_TO_LISTEN = 1

    # Initilize server, this starts a server in the Art-Net port
    a = StupidArtnetServer()

    # For every universe we would like to receive,
    # add a new listener with a optional callback
    # the return is an id for the listener
    u1_listener = a.register_listener(
        UNIVERSE_TO_LISTEN, callback_function=test_callback)

    # print object state
    print(a)

    # giving it some time for the demo
    time.sleep(3)

    # use the listener address to get data without a callback
    buffer = a.get_buffer(u1_listener)

    # Cleanup when you are done
    del a

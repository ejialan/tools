import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.MulticastSocket;
import java.util.HashMap;
import java.util.Map;

/**
 * @author ejialan
 * 
 */
public class MulticastDetector {

    private static final String DEFAULT_MULTICAST_GROUP = "224.2.2.7";
    private static final int DEFAULT_MULTICAST_PORT = 28793;

    private static class PingPang {
        private int index = 0;

        public int getIndex() {
            return index;
        }

        public void increaseIndex() {
            this.index++;
        }
    }

    private static class MulticastPingPang implements Runnable {
        private static final int MAX_PING_NUM = 50;
        String inet;
        int port;
        String groupaddr;
        MulticastSocket multiSocket;
        Map<String, PingPang> knownHosts = new HashMap<String, PingPang>();

        public MulticastPingPang(String inet, int port, String groupaddr) {
            this.inet = inet;
            this.port = port;
            this.groupaddr = groupaddr;
        }

        @Override
        public void run() {
            try {

                InetAddress group = InetAddress.getByName(groupaddr);
                multiSocket = new MulticastSocket(port);
                multiSocket.setInterface(InetAddress.getByName(inet));
                multiSocket.joinGroup(group);

                //say hello to everyone
                String salutations = "hi there";
                DatagramPacket hi = new DatagramPacket(salutations.getBytes(), salutations.length(), group, port);
                multiSocket.send(hi);

                for (;;) {
                    byte[] buf = new byte[1000];
                    DatagramPacket recv = new DatagramPacket(buf, buf.length);
                    multiSocket.receive(recv);

                    String peer = recv.getAddress().getHostAddress();
                    String msg = new String(recv.getData(), recv.getOffset(), recv.getLength());

                    if (peer.equals(inet)) {
                        continue;
                    } else if (msg.equals(salutations)) {
                        ping(peer);
                    } else if (msg.startsWith("ping")) {
                        pang(peer, msg);
                    } else if (msg.startsWith("pang")) {
                        ping(peer, msg);
                    }
                }
            } catch (Exception e) {
                System.err.println("Failed to receive multicast message from " + groupaddr + " at " + inet + ":" + port);
                e.printStackTrace();
                return;
            }
        }
        
        private void ping(String peer) throws Exception {
            System.out.println("New member [" + peer + "] joins at " + inet);
            knownHosts.put(peer, new PingPang());

            String ping = "ping " + knownHosts.get(peer).getIndex();
            DatagramPacket p = new DatagramPacket(ping.getBytes(), ping.length(), InetAddress.getByName(groupaddr), port);
            multiSocket.send(p);
        }

        private void ping(String peer, String pang) throws Exception {
            int index = Integer.parseInt(pang.split(" ")[1]);

            if (index == knownHosts.get(peer).getIndex()) {
                knownHosts.get(peer).increaseIndex();
            } else {
                System.err.println("Want a pang with index " + knownHosts.get(peer).getIndex() + ", but receive an index " + index  + ", msg=[" + pang + "]");
                return;
            }

            if (index == MAX_PING_NUM) {
                System.out.println("------- The multicast traffic from [" + inet + "] to [" + peer + "] is fine!");
            } 
            
            String ping = "ping " + knownHosts.get(peer).getIndex();
            DatagramPacket p = new DatagramPacket(ping.getBytes(), ping.length(), InetAddress.getByName(groupaddr), port);
            multiSocket.send(p);
        }

        private void pang(String peer, String ping) throws Exception {
            int index = Integer.parseInt(ping.split(" ")[1]);
            if (index == 0) {
                knownHosts.put(peer, new PingPang());
            }

            if (index == knownHosts.get(peer).getIndex()) {
                knownHosts.get(peer).increaseIndex();
            } else {
                System.err.println("Want a ping with index " + knownHosts.get(peer).getIndex() + ", but receive an index " + index + ", msg=[" + ping + "]");
                return;
            }

            if (index == MAX_PING_NUM) {
                System.out.println("------- The multicast traffic from [" + inet + "] to [" + peer + "] is fine!");
            } 
            
            String pang = "pang " + index;
            DatagramPacket p = new DatagramPacket(pang.getBytes(), pang.length(), InetAddress.getByName(groupaddr), port);
            multiSocket.send(p);
        }

    }

    /**
     * @param args
     * @throws Exception
     */
    public static void main(String[] args) throws Exception {

        if (args.length == 0) {
            Usage();
            return;
        }

        for (String inet : args) {
            new Thread(new MulticastPingPang(inet, DEFAULT_MULTICAST_PORT, DEFAULT_MULTICAST_GROUP)).start();
        }

        synchronized (args) {
            args.wait();
        }
    }

    private static void Usage() {
        System.out.println(MulticastDetector.class.getCanonicalName() + " <network interface> ...");
        System.out.println("  This tool is used to detect if the multicast traffic netween nodes are wroking.");
        System.out.println("  Run this tool on all nodes and you will get a message if it detects the multicast");
        System.out.println("  traffic to a node is working.");
        System.out.println("  This tool takes a list of IP address as parameter. The IP address represents which");
        System.out.println("  network interface the multicast traffic will go through.");
    }
}

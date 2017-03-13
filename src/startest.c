#include<stdio.h>
#include<unistd.h>
#include<stdlib.h>
#include<glib.h>
#include<pthread.h>
#include"rtcdc.h"
#include"handshake.h"

void rtcdc_e_loop(void *args) {
  struct rtcdc_peer_connection *speer;
  speer = (struct rtcdc_peer_connection *) args;
  rtcdc_loop(speer);
}

int main() {
    struct rtcdc_peer_connection *pc1, *pc2, *pc3, *pc4;
    void onconnectA(struct rtcdc_peer_connection *peer, void *user_data) {
        printf("\nOnConnect of 1->2's");
    }
    void onconnectB(struct rtcdc_peer_connection *peer, void *user_data) {
        printf("\nOnConnect of '1'->3's");
    }
    void *user_data=NULL;

    pc1 = rtcdc_create_peer_connection(NULL, NULL, onconnectA,
            "stun.services.mozilla.com", 3478, user_data);
    
    pc2 = rtcdc_create_peer_connection(NULL, NULL, onconnectA,
            "stun.services.mozilla.com", 3478, user_data);

    pc3 = rtcdc_create_peer_connection(NULL, NULL, onconnectB,
            "stun.services.mozilla.com", 3478, user_data);
    
    pc4 = rtcdc_create_peer_connection(NULL, NULL, onconnectB,
            "stun.services.mozilla.com", 3478, user_data);

    pthread_t tid1, tid2, tid3, tid4; void *res1, *res2, *res3, *res4;
    pthread_create(&tid1, NULL, (void *)rtcdc_e_loop, (void *) pc1);
    pthread_create(&tid2, NULL, (void *)rtcdc_e_loop, (void *) pc2);
    pthread_create(&tid3, NULL, (void *)rtcdc_e_loop, (void *) pc3);
    pthread_create(&tid4, NULL, (void *)rtcdc_e_loop, (void *) pc4);

    handshake(pc1, pc2); // 1->2
    handshake(pc4, pc3); //A new connection considered as 1->3
    // Programmer should keep track of 'peer connections' and consider pc1 and pc4 as 'same' peer '1'.

    pthread_join(tid1, &res1);
    pthread_join(tid2, &res2);
    pthread_join(tid3, &res3);
    pthread_join(tid4, &res4);
    return 0;
}

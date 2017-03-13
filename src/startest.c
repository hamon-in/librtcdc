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
    struct rtcdc_peer_connection *pc1, *pc2, *pc3;
    void onconnect(struct rtcdc_peer_connection *peer, void *user_data) {
        printf("\nOnConnect fired");
    }
    
    void *user_data=NULL;
    printf("\nCreating peer connection...\n");

    pc1 = rtcdc_create_peer_connection(NULL, NULL, onconnect,
            "stun.services.mozilla.com", 3478, user_data);
    
    pc2 = rtcdc_create_peer_connection(NULL, NULL, onconnect,
            "stun.services.mozilla.com", 3478, user_data);

    pc3 = rtcdc_create_peer_connection(NULL, NULL, onconnect,
            "stun.services.mozilla.com", 3478, user_data);

    handshake(pc1, pc2); //onConnect would fire after sometime for peer conn 1->2
    handshake(pc1, pc3); //onConnect doesn't fire for this peer conn 1->3

    pthread_t tid1, tid2, tid3; void *res1;
    pthread_create(&tid1, NULL, (void *)rtcdc_e_loop, (void *) pc1);
    pthread_create(&tid2, NULL, (void *)rtcdc_e_loop, (void *) pc2);
    pthread_create(&tid3, NULL, (void *)rtcdc_e_loop, (void *) pc3);
    pthread_join(tid1, &res1);
    pthread_join(tid2, &res1);
    pthread_join(tid3, &res1);
    return 0;
}

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
    void onmessage(struct rtcdc_data_channel *channel, int datatype, void *data, size_t len, void *user_data) {
        printf("\nData received: %s\n", (char *)data);
    }
    void onopen(struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nDataChannel opened.\n");
        //char *message = "Hello";
        //rtcdc_send_message(channel, RTCDC_DATATYPE_STRING, message, strlen(message));
    }
    void onclose(struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nDataChannel closed\n");
    }
    void onconnect(struct rtcdc_peer_connection *peer, void *user_data) {
        printf("\nOnConnect fired");
        if (peer->role == RTCDC_PEER_ROLE_CLIENT) {
            char label[10];
            snprintf(label, 10, "test-dc-%d", peer->role);
            //rtcdc_create_data_channel(peer, label, "", onopen, onmessage, onclose, (void *)peer);
        }
    }
    void onchannel(struct rtcdc_peer_connection *peer, struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nChannel created: %s\n", channel->label); 
        channel->on_message = onmessage;
    }
    void oncandidate(struct rtcdc_peer_connection *peer, const char *candidate, void *user_data) {
        //printf("\nCandidate found:\n%s\n", g_base64_encode(candidate, strlen(candidate)));
    }
    void *user_data=NULL;
    printf("\nCreating peer connection...\n");

    pc1 = rtcdc_create_peer_connection(onchannel, oncandidate, onconnect,
            "stun.services.mozilla.com", 3478, user_data);
    
    pc2 = rtcdc_create_peer_connection(onchannel, oncandidate, onconnect,
            "stun.services.mozilla.com", 3478, user_data);

    pc3 = rtcdc_create_peer_connection(onchannel, oncandidate, onconnect,
            "stun.services.mozilla.com", 3478, user_data);

    handshake(pc1, pc2);
    handshake(pc1, pc3);

    pthread_t tid1, tid2, tid3; void *res1;
    pthread_create(&tid1, NULL, (void *)rtcdc_e_loop, (void *) pc1);
    pthread_create(&tid2, NULL, (void *)rtcdc_e_loop, (void *) pc2);
    pthread_create(&tid3, NULL, (void *)rtcdc_e_loop, (void *) pc3);
    pthread_join(tid1, &res1);
    pthread_join(tid2, &res1);
    pthread_join(tid3, &res1);
    return 0;
}

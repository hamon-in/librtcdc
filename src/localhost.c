#include<stdio.h>
#include<rtcdc.h>
#include<unistd.h>
#include<stdlib.h>
#include<string.h>
#include<glib.h>
#include<pthread.h>

void rtcdc_e_loop(void *peer) {
    struct rtcdc_peer_connection *speer;
    speer = (struct rtcdc_peer_connection *) peer;
    rtcdc_loop(speer);
}

int main() {
    struct rtcdc_peer_connection *rtcdc_pc1, *rtcdc_pc2;
    void onmessage(struct rtcdc_data_channel *channel, int datatype, void *data, size_t len, void *user_data) {
        printf("\nData received: %s\n", (char *)data);
        rtcdc_destroy_data_channel(channel);
        //destroy the peer connections and quit from here
    }
    void onopen(struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nDataChannel opened.\n");
        char *message = "Hello"; //t
        rtcdc_send_message(channel, RTCDC_DATATYPE_STRING, message, strlen(message));
    }
    void onclose(struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nDataChannel closed!\n");
    }
    void onconnect(struct rtcdc_peer_connection *peer, void *user_data) {
        printf("\nPeer Connection Established.\n");
        rtcdc_create_data_channel(peer, "test-dc", "", onopen, onmessage, onclose, user_data);
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

    rtcdc_pc1 = rtcdc_create_peer_connection(onchannel, oncandidate, onconnect,
            "stun.services.mozilla.com", 3478, user_data);
    
    rtcdc_pc2 = rtcdc_create_peer_connection(onchannel, oncandidate, onconnect,
            "stun.services.mozilla.com", 3478, user_data);

    char *offer1=NULL, *offer2=NULL, *lCSDP1=NULL, *lCSDP2=NULL;
    offer1 = rtcdc_generate_offer_sdp(rtcdc_pc1);

    lCSDP1 = rtcdc_generate_local_candidate_sdp(rtcdc_pc1);
    lCSDP2 = rtcdc_generate_local_candidate_sdp(rtcdc_pc2);

    sleep(3);
    int parse_offer = 0, parse_candidate = 0;
    parse_offer = rtcdc_parse_offer_sdp(rtcdc_pc2, offer1);
    free(offer1);
    if (parse_offer >= 0) {
        offer2 = rtcdc_generate_offer_sdp(rtcdc_pc2);
        rtcdc_parse_offer_sdp(rtcdc_pc1, offer2);
        free(offer2);
    } else {
        printf("\nInvalid remote offer SDP %d\n", parse_offer);
        _exit(1);
        free(offer2);
    }
    
    parse_candidate = rtcdc_parse_candidate_sdp(rtcdc_pc2, lCSDP1);
    if (parse_candidate > 0) {
        printf("\nValid candidates parsed by peer2.\n");
    } else {
        printf("\nInvalid candidates parsed by peer1.\n");
        _exit(1);
    }

    parse_candidate = rtcdc_parse_candidate_sdp(rtcdc_pc1, lCSDP2);
    free(lCSDP1); free(lCSDP2);
    if (parse_candidate > 0) {
        printf("\nValid candidates parsed by peer1.\n");
    } else {
        printf("\nInvalid candidates parsed by peer1.\n");
        _exit(1);
    }


    pthread_t tid1, tid2; void *res;
    pthread_create(&tid1, NULL, (void *)rtcdc_e_loop, (void *) rtcdc_pc1);
    pthread_create(&tid2, NULL, (void *)rtcdc_e_loop, (void *) rtcdc_pc2);
    pthread_join(tid1, &res);
    pthread_join(tid2, &res);

    return 0;
}

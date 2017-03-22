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
    int dc_open = 0;
    struct rtcdc_peer_connection *rtcdc_pc;
    int received_count = 0;
    void onmessage(struct rtcdc_data_channel *channel, int datatype, void *data, size_t len, void *user_data) {
        received_count += 1;
        printf("\nData received: %s. Count: %d\n", (char *) data, received_count);
        //sleep(1);
    }
    void onopen(struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nDataChannel opened.\n");
        dc_open = 1;
    }
    void onclose(struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nDataChannel closed!\n");
        dc_open = 0;
    }
    void onconnect(struct rtcdc_peer_connection *peer, void *user_data) {
        printf("\nPeer Connection Established.\n");
        rtcdc_create_data_channel(peer, "test-dc", "", onopen, onmessage, onclose, user_data);
    }
    
    void onchannel(struct rtcdc_peer_connection *peer, struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nChannel created: %s\n", channel->label); 
        channel->on_message = onmessage;
    }

    void *user_data=NULL;
    printf("\nCreating peer connection...\n");

    rtcdc_pc = rtcdc_create_peer_connection(onchannel, NULL, onconnect,
            "stun.services.mozilla.com", 3478, user_data);
    
    char *offer=NULL, *lCSDP=NULL;
    offer = rtcdc_generate_offer_sdp(rtcdc_pc);
    lCSDP = rtcdc_generate_local_candidate_sdp(rtcdc_pc);
    gchar *b_offer=NULL, *b_lCSDP=NULL;
    b_offer = g_base64_encode((guchar *)offer, strlen(offer));
    free(offer);
    printf("\nOffer SDP: \n%s\n", b_offer);
    g_free(b_offer);
    b_lCSDP = g_base64_encode((guchar *)lCSDP, strlen(lCSDP));
    free(lCSDP);
    printf("\nLocal Candidate: \n%s\n", b_lCSDP);
    g_free(b_lCSDP);
    sleep(3);
    int parse_offer= 0, parse_candidate= 0;
    guchar *dec_remote_sdp_offer=NULL, *dec_remote_candidate=NULL;
    gsize dec_remote_sdp_len = 0, dec_candidate_len= 0;

    printf("\n Enter remote SDP offer (press enter twice): \n");
    gchar *remote_sdp_offer=NULL, *remote_candidate=NULL; size_t len = 0;
    getline(&remote_sdp_offer, &len, stdin);
    dec_remote_sdp_offer = g_base64_decode(remote_sdp_offer, &dec_remote_sdp_len);
    g_free(remote_sdp_offer); len = 0;
    parse_offer = rtcdc_parse_offer_sdp(rtcdc_pc, (gchar *)dec_remote_sdp_offer);
    if (parse_offer >= 0) {
        offer = rtcdc_generate_offer_sdp(rtcdc_pc);
        b_offer = g_base64_encode((guchar *)offer, strlen(offer));
        printf("\nNew Offer SDP: \n%s\n", b_offer);
        g_free(offer);
        g_free(b_offer);
    } else {
        printf("\nInvalid remote offer SDP %d\n", parse_offer);
        _exit(1);
        g_free(offer);
        g_free(b_offer);
    }

    printf("\nEnter remote candidate (press enter twice): \n");
    getline(&remote_candidate, &len, stdin);    
    dec_remote_candidate = g_base64_decode(remote_candidate, &dec_candidate_len);
    g_free(remote_candidate); len = 0;
    parse_candidate = rtcdc_parse_candidate_sdp(rtcdc_pc, (gchar *)dec_remote_candidate);
    if (parse_candidate > 0) {
        printf("\nValid candidates!\n");
    } else {
        printf("\nInvalid candidates!\n");
        _exit(1);
    }
    pthread_t tid;
    pthread_create(&tid, NULL, (void *)rtcdc_e_loop, (void *)rtcdc_pc);
    int count1 = 0;
    while (1)
    {
        if (rtcdc_pc->initialized > 0 && rtcdc_pc->role == RTCDC_PEER_ROLE_CLIENT) {
            struct rtcdc_data_channel *channel;
            if (dc_open == 1) {
                channel = rtcdc_pc->channels[0];
                if (channel->state > RTCDC_CHANNEL_STATE_CLOSED) {
                    gchar* message = "test\0";
                    count1 += 1;
                    printf("%d\n", count1);
                    rtcdc_send_message(channel, RTCDC_DATATYPE_STRING, message, strlen(message) + 1);
                    /*
                    char *q_message = "quit\n";
                    if (strcmp((char *)message, (char *)q_message) == 0)
                      {
                        printf("Quit Recieved");
                        g_free(message);
                        g_free(dec_remote_sdp_offer);
                        g_free(dec_remote_candidate);
                        free(user_data);
                        rtcdc_destroy_peer_connection(rtcdc_pc);
                        break;
                      }
                      */
                    //g_free(message);
                }
            }
        }
        usleep(2 * 1000); //atleast some sleep needed or it segfaults
    }
    //pthread_join(tid, NULL);
    return 0;
}

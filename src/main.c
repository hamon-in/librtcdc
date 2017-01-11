#include<stdio.h>
#include<rtcdc.h>
#include<unistd.h>
#include<stdlib.h>
#include<string.h>
#include<glib.h>

gchar* getlines() {
    size_t len = 0, linesize, inc_size;
    gchar *line, *lines;
    inc_size = 0;
    linesize = 2;
    while (linesize > 1) {
        linesize = getline(&line, &len, stdin);
        size_t strlength = strlen(line);
        size_t old_size = inc_size;
        inc_size += (sizeof(char) * strlength);
        lines = realloc(lines, inc_size);
        for (int i = 0; i < strlength; i++) {
            lines[old_size + i] = line[i];
        }
    }
    lines = realloc(lines, inc_size + 1);
    lines[inc_size + 1] = '\0';
    return lines;
}

int main() {
    struct rtcdc_peer_connection *rtcdc_pc;

    void onconnect(struct rtcdc_peer_connection *peer, void *user_data) {
        printf("\nConnected\n");
    }
    void onchannel(struct rtcdc_peer_connection *peer, struct rtcdc_data_channel *channel, void *user_data) {
        printf("\nChannel created: %s\n", channel->label); 
        //on message send sth
    }
    void oncandidate(struct rtcdc_peer_connection *peer, const char *candidate, void *user_data) {
        //printf("\nCandidate found: %s\n", candidate);
    }

    void *user_data;
    printf("\nCreating peer connection...\n");

    rtcdc_pc = rtcdc_create_peer_connection(onchannel, oncandidate, onconnect,
            "stun.services.mozilla.com", 3478, user_data);
    char *offer, *lCSDP;
    offer = rtcdc_generate_offer_sdp(rtcdc_pc);
    lCSDP = rtcdc_generate_local_candidate_sdp(rtcdc_pc);
    gchar *b_offer, *b_lCSDP;
    b_offer = g_base64_encode(offer, strlen(offer));
    printf("\nOffer SDP: \n%s\n", b_offer);
    b_lCSDP = g_base64_encode(lCSDP, strlen(lCSDP));
    printf("\nLocal Candidate: \n%s\n", b_lCSDP);
    //sleep(3);
    int parse_offer, parse_candidate;
    guchar *dec_remote_sdp_offer, *dec_remote_candidate;
    gsize dec_remote_sdp_len = 0, dec_candidate_len;

    printf("\n Enter remote SDP offer (press enter twice): \n");
    const gchar *remote_sdp_offer, *remote_candidate;
    remote_sdp_offer = getlines();
    dec_remote_sdp_offer = g_base64_decode(remote_sdp_offer, &dec_remote_sdp_len);
    printf("\nDecoded remote SDP:\n%s\n", dec_remote_sdp_offer);
    parse_offer = rtcdc_parse_offer_sdp(rtcdc_pc, dec_remote_sdp_offer);
    if (parse_offer >= 0) {
        offer = rtcdc_generate_offer_sdp(rtcdc_pc); //new one (to be sent to peer)
        b_offer = g_base64_encode(offer, strlen(offer));
        printf("\nNew Offer SDP: \n%s\n", b_offer);
    } else {
        printf("\nInvalid remote offer SDP %d\n", parse_offer);
        _exit(1);
    }

    printf("\nEnter remote candidate (press enter twice): \n");
    remote_candidate = getlines();    
    dec_remote_candidate = g_base64_decode(remote_candidate, &dec_candidate_len);
    printf("\nDecoded remote candidate:\n%s\n", dec_remote_candidate);
    
    //if (dec_remote_sdp_offer[(int) dec_remote_sdp_len] != '\0') {
    //    dec_remote_sdp_offer[(int) dec_remote_sdp_len] = '\0';
    //} ...
    parse_candidate = rtcdc_parse_candidate_sdp(rtcdc_pc, dec_remote_candidate);
    //printf("\nParse SDP offer result: %d\n", parse_offer);
    //printf("\nParse candidate result: %d\n", parse_candidate);
    if (parse_candidate > 0) {
        // valid
        printf("\nValid candidates!\n");
    } else {
        printf("\nInvalid candidates!\n");
        _exit(1);
    }
    g_free(dec_remote_sdp_offer);
    g_free(dec_remote_candidate);
    return 0;
}



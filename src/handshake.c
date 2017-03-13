#include <stdio.h>
#include "rtcdc.h"

int handshake(struct rtcdc_peer_connection *pc1, struct rtcdc_peer_connection *pc2) {
    char *offer1, *newoffer, *can1, *can2;
    offer1 = rtcdc_generate_offer_sdp(pc1);
    if (rtcdc_parse_offer_sdp(pc2, offer1) < 0) {
        printf("\nSDP parse error for peer1's offer on peer2");
        return -1;   
    }
    newoffer = rtcdc_generate_offer_sdp(pc2);
    if (rtcdc_parse_offer_sdp(pc1, newoffer) < 0) {
        printf("\nSDP parse error for peer2's offer on peer1");
        return -1;   
    }
    can1 = rtcdc_generate_local_candidate_sdp(pc1);
    can2 = rtcdc_generate_local_candidate_sdp(pc2);
    if (rtcdc_parse_candidate_sdp(pc1, can2) < 0) {
        printf("\nCandidate parse error of peer2 on peer1");
        return -1;
    }
    if (rtcdc_parse_candidate_sdp(pc2, can1) < 0) {
        printf("\nCandidate parse error of peer1 on peer2");
        return -1;
    }
    return 1;
}

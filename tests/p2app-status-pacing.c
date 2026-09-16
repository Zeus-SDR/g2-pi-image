// SPDX-License-Identifier: GPL-3.0-only
// Copyright (C) 2026 KB2UKA
// Exercise the real status loop with hardware, send, and sleep functions replaced.
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <pthread.h>
#include <setjmp.h>
#include <sys/socket.h>
#include <unistd.h>
#include "threaddata.h"
#include "OutHighPriority.h"
#include "../common/saturndrivers.h"
#include "../common/saturnregisters.h"
#include "LDGATU.h"

bool SDRActive = true, ThreadError = false, MOXAsserted = true;
struct sockaddr_in reply_addr;
static jmp_buf finished;
static unsigned sent, slept_us;
static bool overload;
static unsigned scenario;
static bool pulse_reported;
static bool transient;
static unsigned last_adc_sent;

void ReadStatusRegister(void) {}
unsigned int GetP2PTTKeyInputs(void) { return (scenario == 4 || scenario == 5) ? sent % 2 : 0; }
unsigned int GetADCOverflow(uint16_t *a, uint16_t *b) {
    bool pulse = transient && !pulse_reported && sent == 1 && slept_us >= 500;
    if (pulse) pulse_reported = true;
    /* First ADC read after each send is the poll in sustained scenarios 1/3.
       The pinned loop polls before building the next packet; extra build reads
       remain lower. The higher poll peak must survive those build reads. */
    bool sustained = scenario == 1 || scenario == 3;
    bool poll = sent > 0 && sent != last_adc_sent;
    last_adc_sent = sent;
    *a = pulse ? 32100 : overload ? (sustained && !poll ? 32000 : 32768) : 100;
    *b = 100;
    return overload || pulse ? 1 : 0;
}
unsigned int GetAnalogueIn(unsigned int select) { (void)select; return 0; }
unsigned int GetUserIOBits(void) { return 4; }
uint32_t ReadFIFOMonitorChannel(EDMAStreamSelect channel, bool *over,
    bool *threshold, bool *under, unsigned int *current) {
    (void)channel; *over = *threshold = *under = false; *current = 0; return 0;
}
void RequestATUTune(bool requested) { assert(!requested); }
int MakeSocket(struct ThreadSocketData *data, int id) {
    (void)data; (void)id; abort();
}
int test_usleep(useconds_t us) { slept_us += us; return 0; }
ssize_t test_sendmsg(int socket, const struct msghdr *msg, int flags) {
    (void)socket; (void)flags;
    const unsigned char *p = msg->msg_iov[0].iov_base;
    assert(msg->msg_iov[0].iov_len == 60);
    assert(p[5] == (transient ? sent == 1 : overload));
    if (transient && sent == 1) assert(((unsigned)p[39] << 8 | p[40]) == 32100);
    /* Upstream leaves the first peak uninitialized; assert subsequent packets. */
    if (overload && sent > 0) assert(((unsigned)p[39] << 8 | p[40]) == 32768);
    assert(p[4] == ((scenario == 4 || scenario == 5) ? sent % 2 : 0));
    if (++sent == 100) longjmp(finished, 1);
    return 60;
}
int main(int argc, char **argv) {
    assert(argc == 3);
    scenario = (unsigned)atoi(argv[1]);
    bool patched = atoi(argv[2]) != 0;
    assert(scenario <= 7);
    transient = scenario == 6 || scenario == 7;
    overload = scenario == 1 || scenario == 3 || scenario == 5;
    MOXAsserted = scenario != 2 && scenario != 3 && scenario != 7;
    struct ThreadSocketData data = { .Socketid = -1, .Portid = 1025 };
    if (!setjmp(finished)) OutgoingHighPriority(&data);
    printf("scenario=%u overload=%d packets=%u requested_sleep_us=%u\n", scenario, overload, sent, slept_us);
    /* Repeated overload must not create an unpaced status-send loop. */
    if (scenario == 4 || scenario == 5) return slept_us == 0 ? 0 : 1;
    if (transient) {
        unsigned normal_gap = MOXAsserted ? 1000 : 200000;
        unsigned expected = (sent - 2) * normal_gap + (patched ? 1000 : 500);
        return pulse_reported && slept_us == expected ? 0 : 1;
    }
    unsigned expected = overload ? 500 : MOXAsserted ? 1000 : 200000;
    if (slept_us != (sent - 1) * expected) return 1;
    return 0;
}

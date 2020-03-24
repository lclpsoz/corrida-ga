#include <stdlib.h>
#include <stdio.h>
#include <math.h>


#define COLLISION_NONE 0
#define COLLISION_WALL 1

// Compile with:
// cd src && gcc -std=c11 -Wall -Wextra -pedantic -fPIC -shared -o collisions.so collisions.c && cd ..

// Free memory of ptr.
void freeme(void *ptr) {
    free(ptr);
}

// Free memory of ptr and n intern memory allocations.
void freeme_n(void **ptr, int n) {
    for (int i = 0; i < n; i++)
        free(ptr[i]);
    free(ptr);    
}

//// Custom collision based on cp-geo (Handbook of geometry for
//// competitive programmers).

// Return the cross operation on points represented  by
// float array.
float cross_pointer(float *v, float *w) {
    return v[0]*w[1] - v[1]*w[0];
}

// Return float based on the orientation of the three points
float orient(float *a, float *b, float *c) {
    b[0] -= a[0];
    b[1] -= a[1];
    c[0] -= a[0];
    c[1] -= a[1];
    float ret = cross_pointer(b, c);
    b[0] += a[0];
    b[1] += a[1];
    c[0] += a[0];
    c[1] += a[1];

    return ret;
}

float dot(float *a, float *b) {
    return a[0]*b[0] + a[1]*b[1];
}

int inDisk(float *a, float *b, float *p) {
    a[0] -= p[0];
    a[1] -= p[1];
    b[0] -= p[0];
    b[1] -= p[1];
    int ret = dot(a, b) <= 0;
    a[0] += p[0];
    a[1] += p[1];
    b[0] += p[0];
    b[1] += p[1];

    return ret;
}

// Detects if point p is on segment (a, b)
int onSegment(float *a, float *b, float *p) {
    return orient(a, b, p) == 0 && inDisk(a, b, p);
}

// Intersection between segments (a, b) and (c, d).
int seg_inter(float a[2], float b[2], float c[2], float d[2], float out[2]) {
    float oa = orient(c, d, a),
    ob = orient(c, d, b),
    oc = orient(a, b, c),
    od = orient(a, b, d);

    if(oa*ob < 0 && oc*od < 0) {
        out[0] = (a[0]*ob - b[0]*oa) / (ob-oa);
        out[1] = (a[1]*ob - b[1]*oa) / (ob-oa);
        // printf("!");
        return 1;
    }

    return 0;
}

float dist_sq(float a[2], float b[2]) {
    float dx = a[0]-b[0];
    float dy = a[1]-b[1];
    return dx*dx + dy*dy;
}

// Receive a pointer to segments in a array where every 4 positions
// is a segment.
// Evaluate for each segment on segs if it collide with any wall.
// Returns a int 0 or 1 based on that evaluation.
int *col_circuit(float *segs, int n_segs, float *walls, int n_walls) {
    int *ret = malloc(sizeof(int)*n_segs);
    float out[2];
    for(int i = 0; i < n_segs; i++) {
        float a[] = {segs[4*i], segs[4*i+1]};
        float b[] = {segs[4*i+2], segs[4*i+3]};
        ret[i] = COLLISION_NONE;
        for(int j = 0; j < n_walls; j++) {
            float c[] = {walls[4*j], walls[4*j+1]};
            float d[] = {walls[4*j+2], walls[4*j+3]};
            if(seg_inter(a, b, c, d, out)) {
                // printf("(%f, %f), (%f, %f) AND (%f, %f), (%f, %f)\n",
                //     a[0], a[1], b[0], b[1], c[0], c[1], d[0], d[1]);
                ret[i] = COLLISION_WALL;
                break;
            }
        }
    }
    // printf("RET IN C = ");
    // for(int i = 0; i < n_segs; i++)
    //     printf("%d ", ret[i]);
    // putchar('\n');

    return ret;
}

// Receive a point st and an array with n_segs points.
// Returns array with n_segs floats with distances from
// st to first wall segment collision.
float *col_dist_circuit(float *segs, int n_segs,
                        float *walls, int n_walls) {
    float *dists = malloc(sizeof(int)*n_segs);
    float out[2];
    // printf("st = %.2f %.2f\n", st[0], st[1]);
    for(int i = 0; i < n_segs; i++) {
        float a[] = {segs[4*i], segs[4*i+1]};
        float b[] = {segs[4*i+2], segs[4*i+3]};
        // printf("%d: %.3f %.3f\n", i, b[0], b[1]);
        dists[i] = 1e9;
        float mini = 1e18;
        for(int j = 0; j < n_walls; j++) {
            float c[] = {walls[4*j], walls[4*j+1]};
            float d[] = {walls[4*j+2], walls[4*j+3]};
            if(seg_inter(a, b, c, d, out)) {
                // printf("(%f, %f), (%f, %f) AND (%f, %f), (%f, %f)\n",
                //     a[0], a[1], b[0], b[1], c[0], c[1], d[0], d[1]);
                float d = dist_sq(a, out);
                if(d < mini)
                    mini = d;
            }
        }
        dists[i] = sqrt(mini);
    }
    // printf("RET IN C = ");
    // for(int i = 0; i < n_segs; i++)
    //     printf("%d ", ret[i]);
    // putchar('\n');

    return dists;
}
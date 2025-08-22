"""
// Caernarfon_WS2812_Modes_D678.ino
// Wemos D1 Mini + TerrainTronics Caernarfon Castle
// Inputs: D6 (DAY), D7 (NIGHT) — switches to GND (active-LOW, INPUT_PULLUP)
//         D8 (RED) — switch to 3.3V (active-HIGH, INPUT)
// Default mode = Daylight. Press same mode again = ALL OFF.
// Library: Adafruit_NeoPixel (install via Library Manager).
//
// Board pin recap (Caernarfon):
//  - NEOPIXEL OUT = D3
//  - SERVO1 = D6, SERVO2 = D7, SERVO3 = D8
//  - IR IN = D5, LED = D4
//
// ⚠ Important note about D8 (GPIO15):
//  - ESP8266 bootstraps require GPIO15 LOW at reset for normal boot.
//  - The board hardware includes a 10k pulldown on GPIO15.
//  - To use D8 reliably, wire its switch to 3.3V (active-HIGH).
//  - This means the SERVO header supply voltage must be changed from 5V to 3.3V to avoid overdriving the ESP8266 pin.
//
// Wiring:
//  - DAY and NIGHT switches: connect between GPIO pin and GND. (INPUT_PULLUP, active-LOW)
//  - RED switch: connect between D8 and 3.3V. (INPUT, active-HIGH)
//
// Behavior summary:
//  • Power-up default: DAYLIGHT mode
//  • Press the currently active mode button again → ALL LEDs OFF
//  • From OFF, pressing any mode button → that mode turns ON
//  • If multiple are pressed simultaneously, priority = RED > NIGHT > DAY
//
// -----------------------------------------------------------------------------

#include <Adafruit_NeoPixel.h>

// ---------------- USER CONFIG ----------------
#define NUMPIXELS    300     // <-- set to your strip length
#define BRIGHT_MAX   255    // global cap (0-255)
#define BRIGHT_NIGHT 64     // max brightness at night
#define DATA_PIN     D3     // Caernarfon NEOPIXEL OUT

// Switch pins
#define PIN_DAY      D6   // Servo1 signal (to GND)
#define PIN_NIGHT    D7   // Servo2 signal (to GND)
#define PIN_RED      D8   // Servo3 signal (to 3.3V)

// Debounce
const unsigned long DEBOUNCE_MS = 30;

// Cloud params
float cloudSpeed = 0.10f;
float cloudScale = 3.5f;
uint8_t dayWhite[3] = {255, 245, 230};
uint8_t noonWhite[3] = {220, 235, 255};
uint8_t eveningWhite[3] = {255, 200, 140};

// Night params
uint8_t nightBlue[3] = {10, 20, 60};
uint8_t starWhite[3] = {255, 255, 220};
const uint8_t TWINKLE_CHANCE = 4;
const uint8_t TWINKLE_DECAY  = 6;

Adafruit_NeoPixel strip(NUMPIXELS, DATA_PIN, NEO_GRB + NEO_KHZ800);
uint8_t starLevel[NUMPIXELS];

struct Btn {
  uint8_t pin;
  bool inverted;           // true if using INPUT_PULLUP (active-LOW)
  bool stableState;
  bool lastRead;
  unsigned long lastChange;
  bool lastStable;
};

Btn btnDay   = { PIN_DAY,   true, true, true, 0, true };
Btn btnNight = { PIN_NIGHT, true, true, true, 0, true };
Btn btnRed   = { PIN_RED,   false, false, false, 0, false }; // D8 = active-HIGH

void setupButtons() {
  pinMode(btnDay.pin,   INPUT_PULLUP);
  pinMode(btnNight.pin, INPUT_PULLUP);
  pinMode(btnRed.pin,   INPUT);        // D8 reads HIGH when pressed to 3.3V
}

bool debounceRead(Btn &b) {
  bool raw = digitalRead(b.pin);
  if (b.inverted) raw = !raw;

  if (raw != b.lastRead) {
    b.lastRead = raw;
    b.lastChange = millis();
  }
  if ((millis() - b.lastChange) > DEBOUNCE_MS && b.stableState != b.lastRead) {
    b.stableState = b.lastRead;
  }
  return b.stableState;
}

bool pressedEdge(Btn &b) {
  bool now = debounceRead(b);
  bool edge = (!b.lastStable && now);
  b.lastStable = now;
  return edge;
}

static inline float smoothstep(float x) {
  x = constrain(x, 0.0f, 1.0f);
  return x * x * (3.0f - 2.0f * x);
}

float cloudMaskAt(int i, float t) {
  float u = (float)i / (float)(NUMPIXELS - 1);
  float x = u * (2.0f * PI * cloudScale);

  float a = sinf(x + t);
  float b = sinf(0.7f * x - 1.7f * t + 1.3f);
  float c = sinf(1.3f * x + 0.2f * t + 2.1f);

  float m = (a + b * 0.7f + c * 0.4f) / (1.0f + 0.7f + 0.4f);
  m = 0.5f * (m + 1.0f);
  m = smoothstep(m);
  return 0.55f + 0.45f * m;
}

void blendRGB(const uint8_t a[3], const uint8_t b[3], float t, uint8_t out[3]) {
  t = constrain(t, 0.0f, 1.0f);
  for (int k = 0; k < 3; ++k) {
    out[k] = (uint8_t)(a[k] + t * (b[k] - a[k]));
  }
}

enum Mode { MODE_OFF = -1, MODE_DAY = 0, MODE_NIGHT = 1, MODE_RED = 2 };

void modeDaylight() {
  float t = millis() * 0.001f * cloudSpeed;
  float dayPhase = sinf(millis() * 0.001f * 0.05f) * 0.5f + 0.5f;
  uint8_t dawnToNoon[3]; blendRGB(dayWhite, noonWhite, dayPhase, dawnToNoon);
  uint8_t base[3];       blendRGB(dawnToNoon, eveningWhite, dayPhase, base);

  for (int i = 0; i < NUMPIXELS; ++i) {
    float m = cloudMaskAt(i, t);
    uint8_t r = (uint8_t)(base[0] * m);
    uint8_t g = (uint8_t)(base[1] * m);
    uint8_t b = (uint8_t)(base[2] * m);
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.setBrightness(BRIGHT_MAX);
  strip.show();
}

void modeNight() {
  for (int i = 0; i < NUMPIXELS; ++i) {
    strip.setPixelColor(i, strip.Color(nightBlue[0], nightBlue[1], nightBlue[2]));
  }
  int chance = random(0, 256);
  if (chance < TWINKLE_CHANCE) {
    int idx = random(0, NUMPIXELS);
    starLevel[idx] = 255;
  }
  for (int i = 0; i < NUMPIXELS; ++i) {
    if (starLevel[i] > 0) {
      uint8_t lvl = starLevel[i];
      uint32_t col = strip.Color(
        (uint8_t)((starWhite[0] * (uint16_t)lvl) >> 8),
        (uint8_t)((starWhite[1] * (uint16_t)lvl) >> 8),
        (uint8_t)((starWhite[2] * (uint16_t)lvl) >> 8)
      );
      strip.setPixelColor(i, col);
      starLevel[i] = (lvl > TWINKLE_DECAY) ? (lvl - TWINKLE_DECAY) : 0;
    }
  }
  strip.setBrightness(BRIGHT_NIGHT);
  strip.show();
}

void modeAllRed() {
  for (int i = 0; i < NUMPIXELS; ++i) {
    strip.setPixelColor(i, strip.Color(255, 0, 0));
  }
  strip.setBrightness(BRIGHT_MAX);
  strip.show();
}

void modeOff() {
  strip.clear();
  strip.show();
}

Mode currentMode = MODE_DAY;
Mode lastButtonMode = MODE_DAY;

void setup() {
  randomSeed(ESP.getCycleCount());

  strip.begin();
  strip.show();
  strip.setBrightness(BRIGHT_MAX);

  memset(starLevel, 0, sizeof(starLevel));

  setupButtons();

  pinMode(LED_BUILTIN, OUTPUT);
}

unsigned long lastBeat = 0;

void loop() {
  bool dayEdge   = pressedEdge(btnDay);
  bool nightEdge = pressedEdge(btnNight);
  bool redEdge   = pressedEdge(btnRed);

  Mode pressedMode = MODE_OFF;
  if (redEdge)       pressedMode = MODE_RED;
  else if (nightEdge) pressedMode = MODE_NIGHT;
  else if (dayEdge)   pressedMode = MODE_DAY;

  if (pressedMode != MODE_OFF) {
    if (currentMode == pressedMode) {
      currentMode = MODE_OFF;
    } else {
      currentMode = pressedMode;
      lastButtonMode = pressedMode;
    }
  }

  switch (currentMode) {
    case MODE_DAY:   modeDaylight(); break;
    case MODE_NIGHT: modeNight();    break;
    case MODE_RED:   modeAllRed();   break;
    case MODE_OFF:   modeOff();      break;
  }

  if (millis() - lastBeat > 1000) {
    lastBeat = millis();
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
  }
}
"""
class RecorderWorklet extends AudioWorkletProcessor {
  constructor() {
    super();
    this._bufferSize = 2048;
    this._buffer = new Float32Array(this._bufferSize);
    this._initBuffer();
  }

  _initBuffer() {
    this._bytesWritten = 0;
  }

  _isBufferEmpty() {
    return this._bytesWritten === 0;
  }

  _isBufferFull() {
    return this._bytesWritten === this._bufferSize;
  }

  _appendToBuffer(value) {
    if (this._isBufferFull()) {
      this._flush();
    }
    this._buffer[this._bytesWritten] = value;
    this._bytesWritten += 1;
  }

  _flush() {
    let buffer = this._buffer;
    if (this._bytesWritten < this._bufferSize) {
      buffer = buffer.slice(0, this._bytesWritten);
    }
    
    // Convert float32 to int16
    const int16Buffer = new Int16Array(buffer.length);
    for (let i = 0; i < buffer.length; i++) {
      const s = Math.max(-1, Math.min(1, buffer[i]));
      int16Buffer[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    
    this.port.postMessage(int16Buffer.buffer);
    console.log("🔊 Enviado chunk:", int16Buffer.length);
    this._initBuffer();
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input.length) return true;

    const channel = input[0];
    for (let i = 0; i < channel.length; i++) {
      this._appendToBuffer(channel[i]);
    }

    return true;
  }
}

registerProcessor('recorder-worklet', RecorderWorklet);
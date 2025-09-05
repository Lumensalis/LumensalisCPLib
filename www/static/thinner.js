'use strict';
const startTime = Date.now();

function getNow() {
    const ms = Date.now() - startTime;
    return ms / 1000;
}

class ThinnerChannel   {
    constructor(group, name) {
        this.name = name;
        this.__group = new WeakRef(group);
        this.debounceTime = group.debounceTime;
        this.value = null;
        this.valueChangeTime = 0;
        this.lastWriteTime = 0;
        this.lastWriteValue = null;
        this.debouncedWriteTimerId = null;
    }

    group() {
        return this.__group.deref();
    }

    set( value ) {
        if( value != this.value ) {
            const now = getNow();
            const elapsed = now - this.lastWriteTime;
  
            this.value = value;
            this.valueChangeTime = now;

            if (elapsed > this.debounceTime) {
                if(false) console.log( now.toFixed(3), "set", JSON.stringify(
                {
                    name: this.name, 
                    value: value, oldValue: this.value,
                    elapsed:elapsed.toFixed(3),
                    debouncedWriteTimerId: this.debouncedWriteTimerId,
                    debounceTime: this.debounceTime,
                    lastWriteTime: this.lastWriteTime.toFixed(3),
                    valueChangeTime: this.valueChangeTime.toFixed(3),
                }) );
                this.group().onChannelUpdate(this);

            } else {
                if (this.debouncedWriteTimerId == null) {
                    this._startDebounceTimer();
                }
            }
        }
    }
    _debounceTimeout() {
        const now = getNow();
        console.log( now.toFixed(3), "_debounceTimeout", this.name );
        this.group().onChannelUpdate(this);
         clearTimeout(this.debouncedWriteTimerId);
        this.debouncedWriteTimerId = null;   
    }
    _startDebounceTimer() {
        console.assert( this.debouncedWriteTimerId == null );
        const now = getNow();
        
        const delay = Math.max( 0.0, this.debounceTime - (now - this.lastWriteTime) + 0.0001 );
        console.log( now.toFixed(3), "_startDebounceTimer", this.name, delay );
        this.debouncedWriteTimerId = setTimeout(() => {
            this._debounceTimeout();
        }, delay*1000);
    }

    getValueToWrite() {
        const now = getNow();
        this.lastWriteTime = now;
        this.lastWriteValue = this.value;
        if (this.debouncedWriteTimerId != null) {
            clearTimeout(this.debouncedWriteTimerId);
            this.debouncedWriteTimerId = null;
            console.log( now.toFixed(3), "getValueToWrite + clearTimeout", this.name, this.value  );
        } else {
            console.log( now.toFixed(3), "getValueToWrite", this.name, this.value );
        }
        return this.value;
    }
}

class ThinnerGroup   {
    constructor(thinner, name) {
        this.name = name;
        this.debounceTime = thinner.debounceTime;
        this.channels = {};
        this.onChannelUpdate = null;
        this.__thinner = new WeakRef(thinner);
    }

    thinner() {
        return this.__thinner.deref();
    }

    getChannel( key ) {
        var rv = this.channels[key];
        if( rv == undefined ) {
            rv = new ThinnerChannel(this,key);
            this.channels[key] = rv;
        }
        return this.channels[key];  
    }
}

class Thinner   {
    constructor() {
        this.debounceTime = 0.3;
        this.groups = {};
    }

    getGroup( key ) {
        var rv = this.groups[key];
        if( rv == undefined ) {
            rv = new ThinnerGroup(this,key);
            this.groups[key] = rv;
        }
        return this.groups[key];  
    }
}

function makePanelsThinner(ws) {
    var thinner = new Thinner();

    var updateControlData = thinner.getGroup("control");
    thinner.controls = updateControlData;
    updateControlData.onChannelUpdate = function(channel) {
        const packet = JSON.stringify({
            name: channel.name,
            value: channel.getValueToWrite()
        });
        console.log( "control update", channel.name, packet );
       ws.send( packet );
    }

    var updateTetherData = thinner.getGroup("tether");
    thinner.tethers = updateTetherData;
    updateTetherData.onChannelUpdate = function(channel) {
        const packet = JSON.stringify({
            tether: {
                name: channel.name,
                value: channel.getValueToWrite()
            }
        });
        console.log( "onChannelUpdate", channel.name, packet );
        ws.send( packet );
    }
    return thinner;
}

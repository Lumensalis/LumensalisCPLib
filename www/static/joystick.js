
'use strict';
/* Joystick based on https://codepen.io/jiffy/pen/zrqwON by Jeff Treimport * as createjs from "https://code.createjs.com/1.0.0/createjs.js"leaven */
/**/

function calculateCoords(angle, distance) {
        var coords = {};
        distance = Math.min(distance, 100);  
        var rads = (angle * Math.PI) / 180.0;

        coords.x = distance * Math.cos(rads);
        coords.y = distance * Math.sin(rads);
        
        return coords;
    }

function r01( v ) {
    return v.toFixed(2);
}    

class JoystickControl {
    constructor(elementId) {
        // easal stuff goes hur
        this.elementId = elementId;
        console.log( "creating JoystickControl", elementId, this.elementId );
        this.hashElementId = '#'+this.elementId;
        //var canvas = document.getElementById(this.elementId);
        //var canvas = $(this.hashElementId);
        //this.canvas = canvas;
        //console.log( "JoystickControl canvas", canvas );


        this.myElement = $(this.hashElementId)[0];
        console.log( "JoystickControl myElement", this.myElement );
        //var size =  Math.max( this.myElement.getBoundingClientRect().width,
        //                 this.myElement.getBoundingClientRect().height
        //                 );
        var size = 300;
        console.log( "JoystickControl size", size );
        this.size = size;
        this.szCenter = size / 2;
        this.xCenter = this.szCenter;
        this.yCenter = this.szCenter;
        console.log(JSON.stringify({
            size: this.size,
            szCenter: this.szCenter,
            xCenter: this.xCenter,
            yCenter: this.yCenter
        }));

        this.onJoystickUpdate = null;

        this.stage = new createjs.Stage( this.elementId );

        //this.canvas.addEventListener('joystickMove', this.onJoystickMove.bind(this));

        this.psp = new createjs.Shape();
        this.psp.graphics.beginFill('#a4701bff').drawCircle(this.xCenter, this.yCenter, size/6);

        this.psp.alpha = 0.25;

        this.vertical = new createjs.Shape();
        this.horizontal = new createjs.Shape();
        this.vertical.graphics.beginFill('#ff4d4d').drawRect(this.szCenter, 0, 2, this.size);
        this.horizontal.graphics.beginFill('#ff4d4d').drawRect(0, this.szCenter, this.size, 2);

        this.stage.addChild(this.psp);
        this.stage.addChild(this.vertical);
        this.stage.addChild(this.horizontal);
        var joy = this;

        createjs.Ticker.framerate = 10;
        function updateSelf(event) {
            //console.log( "tick update")
            joy.stage.update();
        }
        createjs.Ticker.addEventListener('tick', updateSelf);

        // create a simple instance
        // by default, it only adds horizontal recognizers
        this.mc = new Hammer(this.myElement);

        this.mc.on("panstart", function(ev) {
            var pos = $(joy.hashElementId).position();
            console.log( "panstart", ev, pos );
            joy.xCenter = joy.psp.x;
            joy.yCenter = joy.psp.y;
            joy.psp.alpha = 0.5;

            console.log( JSON.stringify( {psp:joy.psp.position} ) );
            joy.updateFromEvent(ev);
            joy.stage.update();
        });
        
        // listen to events...
        this.mc.on("panmove", function(ev) {
            //var pos = $(joy.hashElementId).position();

            //var x = (ev.center.x - pos.left - joy.szCenter)/joy.szCenter;
            //var y = -(ev.center.y - pos.top - joy.szCenter)/joy.szCenter;

            //joy.updateJoystickZ({x:x,y:y});

            joy.updateFromEvent(ev);

            var angle = ev.angle;
            var distance = ev.distance; 
            var coords = calculateCoords(angle, distance);
            var evCenter = ev.center;   
            /*
            console.log( JSON.stringify( {
                pos:pos,
                 x:x, y:y,
                  angle:Math.round(angle), distance:Math.round(distance),
                coords:coords,
                 evCenter:evCenter,
                //joyXc:joy.xCenter, joyYc:joy.yCenter
            }));
            */


            joy.psp.x = coords.x;
            joy.psp.y = coords.y;

            joy.psp.alpha = 0.5;
            
            joy.stage.update();
        });

        this.mc.on("panend", function(ev) {
            joy.psp.alpha = 0.25;
            joy.updateJoystickZ({x:0,y:0});
            var target = {x:joy.xCenter,y:joy.yCenter};
            createjs.Tween.get(joy.psp).to(target,750,createjs.Ease.elasticOut);
            console.log( "panend", JSON.stringify( {target:target} ) );
        });
    }

    updateFromEvent( ev ) {
        var pos = $(this.hashElementId).position();

        var x = (ev.center.x - pos.left - this.szCenter)/this.szCenter;
        var y = -(ev.center.y - pos.top - this.szCenter)/this.szCenter;

        if( false ) {
            console.log( "updateFromEvent", JSON.stringify( {eCenter:ev.center,
                // pos:pos, 
                x:x.toFixed(2), y:y.toFixed(2)
            } ) );
        }
        this.updateJoystickZ({x:x,y:y});
    }

    updateJoystickZ(pos) {
        if (this.onJoystickUpdate) {
            this.onJoystickUpdate(pos);
        }

        //$('#xVal').text('X: ' + pos.x);
        //$('#yVal').text('Y: ' + pos.y);
    }


}
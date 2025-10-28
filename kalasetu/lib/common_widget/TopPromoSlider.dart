import 'package:carousel_slider/carousel_slider.dart';
import 'package:flutter/material.dart' hide CarouselController;

class TopPromoSlider extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(left: 10, right: 10),
      child: Container(
          height: 150.0,
          width: double.infinity,
          child: CarouselSlider(
            options: CarouselOptions(
              height: 150.0,
              autoPlay: true,
              enlargeCenterPage: true,
              viewportFraction: 1.0,
            ),
            items: [
              Image.asset(
                "assets/images/promotion__one.png",
                height: 150,
                width: double.infinity,
                fit: BoxFit.cover,
              ),
//              Image.asset("assets/images/promotion_two.png",height: double.infinity,width: double.infinity,),
//              Image.asset("assets/images/promotion_three.png",height: double.infinity,width: double.infinity,),
            ],
          )),
    );
  }
}
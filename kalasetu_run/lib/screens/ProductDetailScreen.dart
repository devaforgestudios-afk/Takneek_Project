import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_ecommerce_app/common_widget/AppBarWidget.dart';
import 'package:flutter_ecommerce_app/common_widget/CircularProgress.dart';
import 'package:flutter_ecommerce_app/models/ProductDetails.dart';
import 'package:flutter_ecommerce_app/utils/Urls.dart';
import 'package:http/http.dart' as http;

class ProductDetailScreen extends StatefulWidget {
  final String slug;

  ProductDetailScreen({Key? key, required this.slug}) : super(key: key);

  @override
  _ProductDetailScreenState createState() => _ProductDetailScreenState();
}

//https://api.evaly.com.bd/core/public/products/leather-backpack-for-women-6dba2a50d/
//https://api.evaly.com.bd/core/public/products/special-women-kids-cotton-panjabi-kameez-by-swapons-world-combo-pack-c8648f9f9/

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFFfafafa),
      appBar: appBarWidget(context),
      body: FutureBuilder<ProductDetails>(
        future: getDetailData(widget.slug),
        builder: (context, AsyncSnapshot<ProductDetails> snapshot) {
          switch (snapshot.connectionState) {
            case ConnectionState.none:
            case ConnectionState.waiting:
              return CircularProgress();
            default:
              if (snapshot.hasError)
                return Text('Error: ${snapshot.error}');
              else
                return createDetailView(context, snapshot);
          }
        },
      ),
      bottomNavigationBar: BottomNavBar(),
    );
  }
}

class BottomNavBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.only(left: 20, right: 10),
      child: Row(
        children: <Widget>[
          Icon(
            Icons.favorite_border,
            color: Color(0xFF5e5e5e),
          ),
          Spacer(),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              elevation: 0,
              backgroundColor: Color(0xFFfef2f2),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.only(
                      topLeft: Radius.circular(10),
                      bottomLeft: Radius.circular(10)),
                  side: BorderSide(color: Color(0xFFfef2f2))),
            ),
            onPressed: () {},
            child: Container(
              padding: EdgeInsets.only(left: 5, right: 5, top: 15, bottom: 15),
              child: Text("Add to cart".toUpperCase(),
                  style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFFff665e))),
            ),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              elevation: 0,
              backgroundColor: Color(0xFFff665e),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.only(
                      topRight: Radius.circular(10),
                      bottomRight: Radius.circular(10)),
                  side: BorderSide(color: Color(0xFFff665e))),
            ),
            onPressed: () {},
            child: Container(
              padding: EdgeInsets.only(left: 5, right: 5, top: 15, bottom: 15),
              child: Text("available at shops".toUpperCase(),
                  style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w400,
                      color: Color(0xFFFFFFFF))),
            ),
          ),
        ],
      ),
    );
  }
}

Widget createDetailView(
    BuildContext context, AsyncSnapshot<ProductDetails> snapshot) {
  final ProductDetails values = snapshot.data!;
  return DetailScreen(
    productDetails: values,
  );
}

class DetailScreen extends StatefulWidget {
  final ProductDetails productDetails;

  DetailScreen({Key? key, required this.productDetails}) : super(key: key);

  @override
  _DetailScreenState createState() => _DetailScreenState();
}

class _DetailScreenState extends State<DetailScreen> {
  @override
  Widget build(BuildContext context) {
    final data = widget.productDetails.data;
    final variants = data?.productVariants ?? <ProductVariants>[];
    final ProductVariants? primaryVariant =
        variants.isNotEmpty ? variants.first : null;
    final images = primaryVariant?.productImages ?? <String>[];
    final String imageUrl = images.isNotEmpty ? images.first : '';
    final String sku = primaryVariant?.sku ?? 'Unavailable';
    final String price = (primaryVariant?.maxPrice?.toString().isNotEmpty ?? false)
        ? primaryVariant!.maxPrice.toString()
        : 'Unavailable';
    final String description =
        primaryVariant?.productDescription ?? 'No description available.';
    final specs = data?.productSpecifications ?? <ProductSpecifications>[];
    return SingleChildScrollView(
      child: Column(
        children: <Widget>[
          /*Image.network(
              widget.productDetails.data.productVariants[0].productImages[0]),*/
          if (imageUrl.isNotEmpty)
            Image.network(
              imageUrl,
              fit: BoxFit.fill,
              loadingBuilder: (BuildContext context, Widget child,
                  ImageChunkEvent? loadingProgress) {
                if (loadingProgress == null) {
                  return child;
                }
                final expected = loadingProgress.expectedTotalBytes;
                final loaded = loadingProgress.cumulativeBytesLoaded;
                final value = expected != null && expected > 0
                    ? loaded / expected
                    : null;
                return Center(
                  child: CircularProgressIndicator(value: value),
                );
              },
            )
          else
            Container(
              height: 250,
              color: const Color(0xFFE0E0E0),
              alignment: Alignment.center,
              child: const Icon(Icons.image_not_supported),
            ),
          SizedBox(
            height: 10,
          ),
          Container(
            padding: EdgeInsets.only(left: 15, right: 15, top: 20, bottom: 20),
            color: Color(0xFFFFFFFF),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Text("SKU".toUpperCase(),
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF565656))),
        Text(sku,
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFFfd0100))),
                Icon(
                  Icons.arrow_forward_ios,
                  color: Color(0xFF999999),
                )
              ],
            ),
          ),
          SizedBox(
            height: 10,
          ),
          Container(
            padding: EdgeInsets.only(left: 15, right: 15, top: 20, bottom: 20),
            color: Color(0xFFFFFFFF),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: <Widget>[
                Text("Price".toUpperCase(),
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF565656))),
        Text(
          "৳ $price".toUpperCase(),
                    style: TextStyle(
            color: price != 'Unavailable'
              ? Color(0xFFf67426)
              : Color(0xFF0dc2cd),
                        fontFamily: 'Roboto-Light.ttf',
                        fontSize: 20,
                        fontWeight: FontWeight.w500)),
              ],
            ),
          ),
          SizedBox(
            height: 10,
          ),
          Container(
            alignment: Alignment.topLeft,
            width: double.infinity,
            padding: EdgeInsets.only(left: 15, right: 15, top: 20, bottom: 20),
            color: Color(0xFFFFFFFF),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text("Description",
                    textAlign: TextAlign.left,
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF565656))),
                SizedBox(
                  height: 15,
                ),
                Text(
          description,
                    textAlign: TextAlign.justify,
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w400,
                        color: Color(0xFF4c4c4c))),
              ],
            ),
          ),
          SizedBox(
            height: 10,
          ),
          Container(
            alignment: Alignment.topLeft,
            width: double.infinity,
            padding: EdgeInsets.only(left: 15, right: 15, top: 20, bottom: 20),
            color: Color(0xFFFFFFFF),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text("Specification",
                    textAlign: TextAlign.left,
                    style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF565656))),
                SizedBox(
                  height: 15,
                ),
                Column(
                  children: generateProductSpecification(context, specs),
                )
              ],
            ),
          )
        ],
      ),
    );
  }

  List<Widget> generateProductSpecification(
      BuildContext context, List<ProductSpecifications> specifications) {
    List<Widget> list = [];
    for (final specification in specifications) {
      Widget element = Container(
        height: 30,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: <Widget>[
            Text(specification.specificationName ?? 'N/A',
                textAlign: TextAlign.left,
                style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w400,
                    color: Color(0xFF444444))),
            Text(specification.specificationValue ?? 'N/A',
                textAlign: TextAlign.left,
                style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w400,
                    color: Color(0xFF212121))),
          ],
        ),
      );
      list.add(element);
    }
    return list;
  }
}

Future<ProductDetails> getDetailData(String slug) async {
  final http.Response response =
      await http.get(Uri.parse(Urls.ROOT_URL + slug));
  final statusCode = response.statusCode;
  final body = json.decode(response.body) as Map<String, dynamic>;
  if (statusCode == 200) {
    return ProductDetails.fromJson(body);
  }
  return ProductDetails();
}
